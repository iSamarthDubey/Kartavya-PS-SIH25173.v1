/**
 * Real-time Updates Store - Manages live data streaming to dashboard widgets
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { DashboardWidget } from '../types'

export interface RealTimeUpdate {
  id: string
  widgetId: string
  data: any
  timestamp: string
  updateType: 'full' | 'partial' | 'append' | 'prepend'
  source: 'websocket' | 'polling' | 'manual'
}

export interface WidgetSubscription {
  widgetId: string
  widgetType: string
  refreshRate: number // milliseconds
  lastUpdate: string
  isActive: boolean
  query?: string
  filters?: any[]
  autoRefresh: boolean
}

interface RealTimeState {
  // Active subscriptions
  subscriptions: WidgetSubscription[]

  // Update queue and history
  updateQueue: RealTimeUpdate[]
  updateHistory: RealTimeUpdate[]

  // Connection state
  isConnected: boolean
  connectionQuality: 'excellent' | 'good' | 'poor' | 'disconnected'
  lastHeartbeat: string | null

  // Performance metrics
  metrics: {
    totalUpdates: number
    updatesPerMinute: number
    averageLatency: number
    failedUpdates: number
    lastMetricsReset: string
  }

  // Configuration
  config: {
    maxUpdateQueueSize: number
    maxHistorySize: number
    defaultRefreshRate: number
    batchSize: number
    throttleDelay: number
    retryAttempts: number
  }

  // Actions
  subscribe: (widget: DashboardWidget, options?: Partial<WidgetSubscription>) => void
  unsubscribe: (widgetId: string) => void
  updateSubscription: (widgetId: string, updates: Partial<WidgetSubscription>) => void

  // Update management
  addUpdate: (update: Omit<RealTimeUpdate, 'id' | 'timestamp'>) => void
  processUpdateQueue: () => Promise<void>
  clearUpdateQueue: () => void
  getUpdatesForWidget: (widgetId: string) => RealTimeUpdate[]

  // Connection management
  setConnectionState: (connected: boolean, quality?: RealTimeState['connectionQuality']) => void
  updateHeartbeat: () => void

  // Metrics
  recordUpdate: (success: boolean, latency?: number) => void
  resetMetrics: () => void
  getMetrics: () => RealTimeState['metrics']

  // Configuration
  updateConfig: (newConfig: Partial<RealTimeState['config']>) => void

  // Utility
  optimizeSubscriptions: () => void
  pauseAllSubscriptions: () => void
  resumeAllSubscriptions: () => void
}

export const useRealTimeStore = create<RealTimeState>()(
  persist(
    (set, get) => ({
      // Initial state
      subscriptions: [],
      updateQueue: [],
      updateHistory: [],

      isConnected: false,
      connectionQuality: 'disconnected',
      lastHeartbeat: null,

      metrics: {
        totalUpdates: 0,
        updatesPerMinute: 0,
        averageLatency: 0,
        failedUpdates: 0,
        lastMetricsReset: new Date().toISOString(),
      },

      config: {
        maxUpdateQueueSize: 100,
        maxHistorySize: 500,
        defaultRefreshRate: 30000, // 30 seconds
        batchSize: 10,
        throttleDelay: 1000, // 1 second
        retryAttempts: 3,
      },

      // Actions
      subscribe: (widget: DashboardWidget, options = {}) => {
        const state = get()
        const existingSubscription = state.subscriptions.find(s => s.widgetId === widget.id)

        if (existingSubscription) {
          // Update existing subscription
          set({
            subscriptions: state.subscriptions.map(s =>
              s.widgetId === widget.id ? { ...s, ...options, isActive: true } : s
            ),
          })
        } else {
          // Create new subscription
          const newSubscription: WidgetSubscription = {
            widgetId: widget.id,
            widgetType: widget.type,
            refreshRate: options.refreshRate || state.config.defaultRefreshRate,
            lastUpdate: new Date().toISOString(),
            isActive: true,
            autoRefresh: options.autoRefresh ?? true,
            ...options,
          }

          set({
            subscriptions: [...state.subscriptions, newSubscription],
          })
        }
      },

      unsubscribe: (widgetId: string) => {
        const state = get()
        set({
          subscriptions: state.subscriptions.filter(s => s.widgetId !== widgetId),
        })
      },

      updateSubscription: (widgetId: string, updates: Partial<WidgetSubscription>) => {
        const state = get()
        set({
          subscriptions: state.subscriptions.map(s =>
            s.widgetId === widgetId ? { ...s, ...updates, lastUpdate: new Date().toISOString() } : s
          ),
        })
      },

      // Update management
      addUpdate: (update: Omit<RealTimeUpdate, 'id' | 'timestamp'>) => {
        const state = get()
        const newUpdate: RealTimeUpdate = {
          ...update,
          id: `update_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
        }

        // Add to queue
        const newQueue = [...state.updateQueue, newUpdate].slice(-state.config.maxUpdateQueueSize)

        // Add to history
        const newHistory = [...state.updateHistory, newUpdate].slice(-state.config.maxHistorySize)

        set({
          updateQueue: newQueue,
          updateHistory: newHistory,
        })

        // Auto-process if queue is getting full
        if (newQueue.length >= state.config.batchSize) {
          setTimeout(() => get().processUpdateQueue(), state.config.throttleDelay)
        }
      },

      processUpdateQueue: async () => {
        const state = get()
        if (state.updateQueue.length === 0) return

        const updates = state.updateQueue.slice(0, state.config.batchSize)

        try {
          // Group updates by widget for batch processing
          const updatesByWidget = updates.reduce(
            (acc, update) => {
              if (!acc[update.widgetId]) {
                acc[update.widgetId] = []
              }
              acc[update.widgetId].push(update)
              return acc
            },
            {} as Record<string, RealTimeUpdate[]>
          )

          // Process updates for each widget
          for (const [widgetId, widgetUpdates] of Object.entries(updatesByWidget)) {
            await processWidgetUpdates(widgetId, widgetUpdates)
          }

          // Remove processed updates from queue
          set({
            updateQueue: state.updateQueue.slice(updates.length),
          })

          // Record successful processing
          get().recordUpdate(true)
        } catch (error) {
          console.error('Error processing update queue:', error)
          get().recordUpdate(false)
        }
      },

      clearUpdateQueue: () => {
        set({ updateQueue: [] })
      },

      getUpdatesForWidget: (widgetId: string) => {
        const state = get()
        return state.updateHistory.filter(update => update.widgetId === widgetId)
      },

      // Connection management
      setConnectionState: (connected: boolean, quality = 'disconnected') => {
        set({
          isConnected: connected,
          connectionQuality: connected ? quality : 'disconnected',
        })
      },

      updateHeartbeat: () => {
        set({ lastHeartbeat: new Date().toISOString() })
      },

      // Metrics
      recordUpdate: (success: boolean, latency = 0) => {
        const state = get()
        const now = new Date()
        const resetTime = new Date(state.metrics.lastMetricsReset)
        const minutesSinceReset = (now.getTime() - resetTime.getTime()) / (1000 * 60)

        set({
          metrics: {
            ...state.metrics,
            totalUpdates: state.metrics.totalUpdates + 1,
            updatesPerMinute: state.metrics.totalUpdates / Math.max(minutesSinceReset, 1),
            averageLatency:
              latency > 0
                ? (state.metrics.averageLatency + latency) / 2
                : state.metrics.averageLatency,
            failedUpdates: success ? state.metrics.failedUpdates : state.metrics.failedUpdates + 1,
          },
        })
      },

      resetMetrics: () => {
        set({
          metrics: {
            totalUpdates: 0,
            updatesPerMinute: 0,
            averageLatency: 0,
            failedUpdates: 0,
            lastMetricsReset: new Date().toISOString(),
          },
        })
      },

      getMetrics: () => {
        return get().metrics
      },

      // Configuration
      updateConfig: (newConfig: Partial<RealTimeState['config']>) => {
        const state = get()
        set({
          config: { ...state.config, ...newConfig },
        })
      },

      // Utility
      optimizeSubscriptions: () => {
        const state = get()

        // Remove inactive subscriptions older than 5 minutes
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString()

        set({
          subscriptions: state.subscriptions.filter(
            s => s.isActive || s.lastUpdate > fiveMinutesAgo
          ),
        })
      },

      pauseAllSubscriptions: () => {
        const state = get()
        set({
          subscriptions: state.subscriptions.map(s => ({ ...s, isActive: false })),
        })
      },

      resumeAllSubscriptions: () => {
        const state = get()
        set({
          subscriptions: state.subscriptions.map(s => ({ ...s, isActive: true })),
        })
      },
    }),
    {
      name: 'synrgy-realtime-store',
      partialize: state => ({
        // Only persist configuration and subscription preferences
        config: state.config,
        subscriptions: state.subscriptions.map(s => ({
          ...s,
          isActive: false, // Reset active state on reload
        })),
      }),
    }
  )
)

// Helper function to process widget updates
async function processWidgetUpdates(widgetId: string, updates: RealTimeUpdate[]) {
  // This would typically update the widget's data in the hybrid store
  // For now, we'll dispatch a custom event that widgets can listen to

  const event = new CustomEvent('widget-update', {
    detail: {
      widgetId,
      updates,
      timestamp: new Date().toISOString(),
    },
  })

  window.dispatchEvent(event)
}

// Selectors for better performance
export const useRealTimeConnection = () => {
  return useRealTimeStore(state => ({
    isConnected: state.isConnected,
    connectionQuality: state.connectionQuality,
    lastHeartbeat: state.lastHeartbeat,
    setConnectionState: state.setConnectionState,
    updateHeartbeat: state.updateHeartbeat,
  }))
}

export const useWidgetSubscriptions = () => {
  return useRealTimeStore(state => ({
    subscriptions: state.subscriptions,
    subscribe: state.subscribe,
    unsubscribe: state.unsubscribe,
    updateSubscription: state.updateSubscription,
  }))
}

export const useRealTimeMetrics = () => {
  return useRealTimeStore(state => ({
    metrics: state.metrics,
    recordUpdate: state.recordUpdate,
    resetMetrics: state.resetMetrics,
    getMetrics: state.getMetrics,
  }))
}

export default useRealTimeStore
