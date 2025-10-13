/**
 * Hybrid Mode Store - Manages the state for hybrid dashboard-chat interface
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { VisualPayload, DashboardWidget, ConversationContext, ChatMessage } from '../types'

interface HybridModeState {
  // Layout state
  isHybridMode: boolean
  layout: 'dashboard-only' | 'chat-only' | 'split-view' | 'overlay'
  splitRatio: number // 0.0 to 1.0, how much space dashboard takes

  // Dashboard state
  pinnedWidgets: DashboardWidget[]
  widgetLayout: { [widgetId: string]: { x: number; y: number; w: number; h: number } }
  dashboardContext: ConversationContext | null

  // Chat state
  chatContext: ConversationContext | null
  pendingPinRequests: { [messageId: string]: VisualPayload }
  chatPanelCollapsed: boolean

  // Synchronization state
  activeContextSync: boolean
  lastSyncTimestamp: string | null
  contextBridge: { [contextId: string]: any }
  focusedSession: {
    type: 'widget' | 'chat' | 'dashboard'
    id: string
    context: ConversationContext
    spawnQuery?: string
  } | null
  contextHistory: Array<{
    id: string
    type: 'sync' | 'bridge' | 'spawn'
    from: 'dashboard' | 'chat'
    to: 'dashboard' | 'chat'
    context: ConversationContext
    timestamp: string
  }>

  // Actions
  setHybridMode: (enabled: boolean) => void
  setLayout: (layout: HybridModeState['layout']) => void
  setSplitRatio: (ratio: number) => void

  // Widget management
  pinWidget: (widget: DashboardWidget) => void
  unpinWidget: (widgetId: string) => void
  updateWidgetPosition: (
    widgetId: string,
    position: { x: number; y: number; w: number; h: number }
  ) => void
  clearAllWidgets: () => void

  // Context management
  setDashboardContext: (context: ConversationContext) => void
  setChatContext: (context: ConversationContext) => void
  syncContexts: () => void
  bridgeContext: (fromMode: 'dashboard' | 'chat', contextData: any) => void

  // Pin management
  addPendingPin: (messageId: string, payload: VisualPayload) => void
  confirmPin: (messageId: string, widgetOverrides?: Partial<DashboardWidget>) => void
  cancelPin: (messageId: string) => void

  // Chat panel management
  toggleChatPanel: () => void
  setChatPanelCollapsed: (collapsed: boolean) => void

  // Widget spawning from dashboard
  spawnChatFromWidget: (widgetId: string, query: string) => void

  // Focused session management
  startFocusedSession: (
    type: 'widget' | 'chat' | 'dashboard',
    id: string,
    context: ConversationContext,
    spawnQuery?: string
  ) => void
  endFocusedSession: () => void
  updateFocusedSession: (context: ConversationContext) => void

  // Context history management
  addContextHistoryEntry: (
    entry: Omit<HybridModeState['contextHistory'][0], 'id' | 'timestamp'>
  ) => void
  clearContextHistory: () => void
  getContextHistoryForEntity: (entityId: string) => HybridModeState['contextHistory']

  // Utility
  generateWidgetFromPayload: (payload: VisualPayload, messageId: string) => DashboardWidget
  findOptimalPosition: (widget?: DashboardWidget) => {
    row: number
    col: number
    width: number
    height: number
  }
  optimizeLayout: () => void
}

export const useHybridStore = create<HybridModeState>()(
  persist(
    (set, get) => ({
      // Initial state
      isHybridMode: false,
      layout: 'split-view',
      splitRatio: 0.7, // 70% dashboard, 30% chat

      pinnedWidgets: [],
      widgetLayout: {},
      dashboardContext: null,

      chatContext: null,
      pendingPinRequests: {},
      chatPanelCollapsed: false,

      activeContextSync: true,
      lastSyncTimestamp: null,
      contextBridge: {},
      focusedSession: null,
      contextHistory: [],

      // Actions
      setHybridMode: (enabled: boolean) => {
        set({ isHybridMode: enabled })

        // Auto-adjust layout when entering hybrid mode
        if (enabled) {
          const currentLayout = get().layout
          if (currentLayout === 'dashboard-only' || currentLayout === 'chat-only') {
            set({ layout: 'split-view' })
          }
        }
      },

      setLayout: (layout: HybridModeState['layout']) => {
        set({ layout })

        // Auto-enable hybrid mode for relevant layouts
        if (layout === 'split-view' || layout === 'overlay') {
          set({ isHybridMode: true })
        }
      },

      setSplitRatio: (ratio: number) => {
        const clampedRatio = Math.max(0.2, Math.min(0.8, ratio)) // Keep between 20-80%
        set({ splitRatio: clampedRatio })
      },

      // Widget management
      pinWidget: (widget: DashboardWidget) => {
        const state = get()
        const existingWidget = state.pinnedWidgets.find(w => w.id === widget.id)

        if (existingWidget) {
          // Update existing widget
          set({
            pinnedWidgets: state.pinnedWidgets.map(w =>
              w.id === widget.id ? { ...w, ...widget, last_updated: new Date().toISOString() } : w
            ),
          })
        } else {
          // Add new widget
          const optimalPos = get().findOptimalPosition(widget)
          const newWidget = {
            ...widget,
            last_updated: new Date().toISOString(),
            position: widget.position || {
              row: optimalPos.row,
              col: optimalPos.col,
              width: optimalPos.width,
              height: optimalPos.height,
            },
          }

          set({
            pinnedWidgets: [...state.pinnedWidgets, newWidget],
            widgetLayout: {
              ...state.widgetLayout,
              [newWidget.id]: {
                x: newWidget.position.col,
                y: newWidget.position.row,
                w: newWidget.position.width,
                h: newWidget.position.height,
              },
            },
          })
        }

        // Update sync timestamp
        set({ lastSyncTimestamp: new Date().toISOString() })
      },

      unpinWidget: (widgetId: string) => {
        const state = get()
        set({
          pinnedWidgets: state.pinnedWidgets.filter(w => w.id !== widgetId),
          widgetLayout: Object.fromEntries(
            Object.entries(state.widgetLayout).filter(([id]) => id !== widgetId)
          ),
        })
      },

      updateWidgetPosition: (
        widgetId: string,
        position: { x: number; y: number; w: number; h: number }
      ) => {
        const state = get()
        set({
          widgetLayout: {
            ...state.widgetLayout,
            [widgetId]: position,
          },
          pinnedWidgets: state.pinnedWidgets.map(w =>
            w.id === widgetId
              ? {
                  ...w,
                  position: {
                    row: position.y,
                    col: position.x,
                    width: position.w,
                    height: position.h,
                  },
                }
              : w
          ),
        })
      },

      clearAllWidgets: () => {
        set({
          pinnedWidgets: [],
          widgetLayout: {},
          pendingPinRequests: {},
        })
      },

      // Context management
      setDashboardContext: (context: ConversationContext) => {
        set({ dashboardContext: context })

        // Auto-sync if enabled
        if (get().activeContextSync) {
          get().syncContexts()
        }
      },

      setChatContext: (context: ConversationContext) => {
        set({ chatContext: context })

        // Auto-sync if enabled
        if (get().activeContextSync) {
          get().syncContexts()
        }
      },

      syncContexts: () => {
        const state = get()

        if (!state.activeContextSync) return

        const { dashboardContext, chatContext, focusedSession } = state

        // Include focused session context in merge
        const focusedContext = focusedSession?.context

        // Merge contexts intelligently
        const mergedContext = {
          conversation_id:
            chatContext?.conversation_id ||
            dashboardContext?.conversation_id ||
            focusedContext?.conversation_id ||
            'hybrid_session',
          history: [
            ...(dashboardContext?.history || []),
            ...(chatContext?.history || []),
            ...(focusedContext?.history || []),
          ].slice(-30), // Keep last 30 messages for better context
          entities: {
            ...dashboardContext?.entities,
            ...chatContext?.entities,
            ...focusedContext?.entities,
          },
          filters: [
            ...(dashboardContext?.filters || []),
            ...(chatContext?.filters || []),
            ...(focusedContext?.filters || []),
          ],
          time_range:
            focusedContext?.time_range || chatContext?.time_range || dashboardContext?.time_range,
          metadata: {
            ...dashboardContext?.metadata,
            ...chatContext?.metadata,
            ...focusedContext?.metadata,
            hybrid_sync: true,
            last_sync: new Date().toISOString(),
            focused_session: focusedSession
              ? {
                  type: focusedSession.type,
                  id: focusedSession.id,
                  spawn_query: focusedSession.spawnQuery,
                }
              : undefined,
          },
        }

        set({
          dashboardContext: mergedContext,
          chatContext: mergedContext,
          lastSyncTimestamp: new Date().toISOString(),
        })

        // Add sync entry to history
        get().addContextHistoryEntry({
          type: 'sync',
          from: 'dashboard',
          to: 'chat',
          context: mergedContext,
        })
      },

      bridgeContext: (fromMode: 'dashboard' | 'chat', contextData: any) => {
        const state = get()
        const bridgeId = `bridge_${Date.now()}`

        set({
          contextBridge: {
            ...state.contextBridge,
            [bridgeId]: {
              from: fromMode,
              data: contextData,
              timestamp: new Date().toISOString(),
            },
          },
        })

        // Apply context to target mode
        if (fromMode === 'dashboard') {
          // Apply to chat context
          const updatedChatContext = {
            ...state.chatContext,
            ...contextData,
            metadata: {
              ...state.chatContext?.metadata,
              bridge_from: 'dashboard',
              bridge_id: bridgeId,
            },
          }
          set({ chatContext: updatedChatContext })
        } else {
          // Apply to dashboard context
          const updatedDashboardContext = {
            ...state.dashboardContext,
            ...contextData,
            metadata: {
              ...state.dashboardContext?.metadata,
              bridge_from: 'chat',
              bridge_id: bridgeId,
            },
          }
          set({ dashboardContext: updatedDashboardContext })
        }
      },

      // Pin management
      addPendingPin: (messageId: string, payload: VisualPayload) => {
        const state = get()
        set({
          pendingPinRequests: {
            ...state.pendingPinRequests,
            [messageId]: payload,
          },
        })
      },

      confirmPin: (messageId: string, widgetOverrides?: Partial<DashboardWidget>) => {
        const state = get()
        const payload = state.pendingPinRequests[messageId]

        if (!payload) return

        // Generate widget from payload
        const widget = get().generateWidgetFromPayload(payload, messageId)

        // Apply any overrides
        const finalWidget = { ...widget, ...widgetOverrides }

        // Pin the widget
        get().pinWidget(finalWidget)

        // Remove from pending
        set({
          pendingPinRequests: Object.fromEntries(
            Object.entries(state.pendingPinRequests).filter(([id]) => id !== messageId)
          ),
        })
      },

      cancelPin: (messageId: string) => {
        const state = get()
        set({
          pendingPinRequests: Object.fromEntries(
            Object.entries(state.pendingPinRequests).filter(([id]) => id !== messageId)
          ),
        })
      },

      // Chat panel management
      toggleChatPanel: () => {
        set(state => ({ chatPanelCollapsed: !state.chatPanelCollapsed }))
      },

      setChatPanelCollapsed: (collapsed: boolean) => {
        set({ chatPanelCollapsed: collapsed })
      },

      // Widget spawning from dashboard
      spawnChatFromWidget: (widgetId: string, query: string) => {
        const state = get()
        const widget = state.pinnedWidgets.find(w => w.id === widgetId)

        if (!widget) return

        // Create context from widget
        const contextData = {
          conversation_id: `widget_${widgetId}_${Date.now()}`,
          history: [],
          entities: {},
          filters: [],
          metadata: {
            spawned_from_widget: widgetId,
            widget_title: widget.title,
            widget_type: widget.type,
            spawn_query: query,
            spawn_timestamp: new Date().toISOString(),
          },
        }

        // Bridge context to chat
        get().bridgeContext('dashboard', contextData)

        // Show chat panel if collapsed
        if (state.chatPanelCollapsed) {
          set({ chatPanelCollapsed: false })
        }

        // Switch to hybrid mode if not already
        if (!state.isHybridMode) {
          set({ isHybridMode: true, layout: 'split-view' })
        }
      },

      // Focused session management
      startFocusedSession: (
        type: 'widget' | 'chat' | 'dashboard',
        id: string,
        context: ConversationContext,
        spawnQuery?: string
      ) => {
        const sessionId = `session_${type}_${id}_${Date.now()}`

        set({
          focusedSession: {
            type,
            id,
            context,
            spawnQuery,
          },
        })

        // Add to context history
        get().addContextHistoryEntry({
          type: 'spawn',
          from: type === 'widget' ? 'dashboard' : (type as 'dashboard' | 'chat'),
          to: type === 'widget' ? 'chat' : (type as 'dashboard' | 'chat'),
          context,
        })

        // Auto-sync contexts
        if (get().activeContextSync) {
          get().syncContexts()
        }
      },

      endFocusedSession: () => {
        const state = get()

        if (state.focusedSession) {
          // Add end session to history
          get().addContextHistoryEntry({
            type: 'sync',
            from:
              state.focusedSession.type === 'widget'
                ? 'dashboard'
                : (state.focusedSession.type as 'dashboard' | 'chat'),
            to:
              state.focusedSession.type === 'widget'
                ? 'chat'
                : (state.focusedSession.type as 'dashboard' | 'chat'),
            context: state.focusedSession.context,
          })
        }

        set({ focusedSession: null })
      },

      updateFocusedSession: (context: ConversationContext) => {
        const state = get()

        if (!state.focusedSession) return

        set({
          focusedSession: {
            ...state.focusedSession,
            context,
          },
        })

        // Auto-sync if enabled
        if (state.activeContextSync) {
          get().syncContexts()
        }
      },

      // Context history management
      addContextHistoryEntry: (
        entry: Omit<HybridModeState['contextHistory'][0], 'id' | 'timestamp'>
      ) => {
        const state = get()
        const historyEntry = {
          ...entry,
          id: `history_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
        }

        const updatedHistory = [...state.contextHistory, historyEntry].slice(-50) // Keep last 50 entries

        set({ contextHistory: updatedHistory })
      },

      clearContextHistory: () => {
        set({ contextHistory: [] })
      },

      getContextHistoryForEntity: (entityId: string): HybridModeState['contextHistory'] => {
        const state = get()
        return state.contextHistory.filter(
          entry => entry.context.entities && Object.keys(entry.context.entities).includes(entityId)
        )
      },

      // Utility functions
      generateWidgetFromPayload: (payload: VisualPayload, messageId: string): DashboardWidget => {
        const widgetId = `widget_${messageId}_${Date.now()}`

        if (payload.type === 'composite' && payload.cards) {
          // Create a composite widget
          return {
            id: widgetId,
            type: 'chart', // Default to chart for composite
            title: payload.cards[0]?.title || 'Dashboard Widget',
            data: payload,
            config: {
              layout: 'composite',
              cards: payload.cards,
            },
            position: {
              row: 0,
              col: 0,
              width: 2,
              height: 2,
            },
            last_updated: new Date().toISOString(),
          }
        } else {
          // Create a single widget
          return {
            id: widgetId,
            type:
              payload.type === 'chart'
                ? 'chart'
                : payload.type === 'table'
                  ? 'table'
                  : payload.type === 'narrative'
                    ? 'insight_feed'
                    : 'summary_card',
            title: (payload as any).title || 'Widget',
            data: payload,
            config: (payload as any).config || {},
            position: {
              row: 0,
              col: 0,
              width: 1,
              height: 1,
            },
            last_updated: new Date().toISOString(),
          }
        }
      },

      findOptimalPosition: (
        widget?: DashboardWidget
      ): { row: number; col: number; width: number; height: number } => {
        const state = get()
        const existingPositions = Object.values(state.widgetLayout)

        // Simple grid placement algorithm
        const gridCols = 4
        let row = 0
        let col = 0

        // Find first available position
        while (existingPositions.some(pos => pos.x === col && pos.y === row)) {
          col++
          if (col >= gridCols) {
            col = 0
            row++
          }
        }

        // Default widget size
        const width = widget?.type === 'chart' ? 2 : 1
        const height = widget?.type === 'table' ? 2 : 1

        return {
          row,
          col,
          width,
          height,
        }
      },

      optimizeLayout: () => {
        const state = get()
        const widgets = state.pinnedWidgets

        // Simple layout optimization - compact widgets upward and leftward
        const optimizedLayout = { ...state.widgetLayout }

        widgets.forEach(widget => {
          const currentPos = optimizedLayout[widget.id]
          if (!currentPos) return

          // Try to move widget to optimal position
          const optimalPos = get().findOptimalPosition(widget)
          optimizedLayout[widget.id] = {
            x: optimalPos.col,
            y: optimalPos.row,
            w: currentPos.w || optimalPos.width,
            h: currentPos.h || optimalPos.height,
          }
        })

        set({ widgetLayout: optimizedLayout })
      },
    }),
    {
      name: 'synrgy-hybrid-store',
      partialize: state => ({
        // Persist essential hybrid state
        isHybridMode: state.isHybridMode,
        layout: state.layout,
        splitRatio: state.splitRatio,
        pinnedWidgets: state.pinnedWidgets,
        widgetLayout: state.widgetLayout,
        activeContextSync: state.activeContextSync,
        chatPanelCollapsed: state.chatPanelCollapsed,
      }),
    }
  )
)

// Selectors for optimal performance
export const useHybridMode = () => {
  return useHybridStore(state => ({
    isHybridMode: state.isHybridMode,
    layout: state.layout,
    setHybridMode: state.setHybridMode,
    setLayout: state.setLayout,
  }))
}

export const useWidgetManagement = () => {
  return useHybridStore(state => ({
    pinnedWidgets: state.pinnedWidgets,
    widgetLayout: state.widgetLayout,
    pinWidget: state.pinWidget,
    unpinWidget: state.unpinWidget,
    updateWidgetPosition: state.updateWidgetPosition,
    clearAllWidgets: state.clearAllWidgets,
    optimizeLayout: state.optimizeLayout,
  }))
}

export const useContextSync = () => {
  return useHybridStore(state => ({
    activeContextSync: state.activeContextSync,
    dashboardContext: state.dashboardContext,
    chatContext: state.chatContext,
    focusedSession: state.focusedSession,
    contextHistory: state.contextHistory,
    syncContexts: state.syncContexts,
    bridgeContext: state.bridgeContext,
    startFocusedSession: state.startFocusedSession,
    endFocusedSession: state.endFocusedSession,
    updateFocusedSession: state.updateFocusedSession,
    addContextHistoryEntry: state.addContextHistoryEntry,
    clearContextHistory: state.clearContextHistory,
    getContextHistoryForEntity: state.getContextHistoryForEntity,
  }))
}
