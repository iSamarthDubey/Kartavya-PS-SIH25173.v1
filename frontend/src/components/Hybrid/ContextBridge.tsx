/**
 * Context Bridge Component - Manages bidirectional context synchronization
 */

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeftRight,
  History,
  Settings,
  Target,
  MessageCircle,
  BarChart3,
  Layers,
  Clock,
  Filter,
  Users,
  Zap,
  Eye,
  X
} from 'lucide-react'
import { useHybridStore, useContextSync } from '../../stores/hybridStore'
import type { ConversationContext } from '../../types'

interface ContextBridgeProps {
  className?: string
  showCompact?: boolean
  onContextSelect?: (context: ConversationContext) => void
}

export const ContextBridge: React.FC<ContextBridgeProps> = ({
  className = '',
  showCompact = false,
  onContextSelect
}) => {
  const {
    activeContextSync,
    dashboardContext,
    chatContext,
    focusedSession,
    contextHistory,
    syncContexts,
    bridgeContext,
    startFocusedSession,
    endFocusedSession,
    clearContextHistory
  } = useContextSync()

  const { pinnedWidgets } = useHybridStore(state => ({
    pinnedWidgets: state.pinnedWidgets
  }))

  const [showHistory, setShowHistory] = useState(false)
  const [selectedHistoryEntry, setSelectedHistoryEntry] = useState<string | null>(null)

  // Auto-sync when contexts change
  useEffect(() => {
    if (activeContextSync && (dashboardContext || chatContext)) {
      const timer = setTimeout(() => syncContexts(), 1000)
      return () => clearTimeout(timer)
    }
  }, [dashboardContext, chatContext, activeContextSync, syncContexts])

  const formatContextSummary = (context: ConversationContext | null) => {
    if (!context) return { entities: 0, filters: 0, messages: 0 }
    
    return {
      entities: Object.keys(context.entities || {}).length,
      filters: (context.filters || []).length,
      messages: (context.history || []).length
    }
  }

  const dashboardSummary = formatContextSummary(dashboardContext)
  const chatSummary = formatContextSummary(chatContext)

  const handleManualSync = () => {
    syncContexts()
  }

  const handleBridgeFromDashboard = () => {
    if (dashboardContext) {
      bridgeContext('dashboard', dashboardContext)
    }
  }

  const handleBridgeFromChat = () => {
    if (chatContext) {
      bridgeContext('chat', chatContext)
    }
  }

  const handleSpawnFocusedChat = (widgetId: string) => {
    const widget = pinnedWidgets.find(w => w.id === widgetId)
    if (!widget) return

    const focusContext: ConversationContext = {
      conversation_id: `widget_focus_${widgetId}`,
      history: [],
      entities: {},
      filters: [],
      metadata: {
        focused_widget: widgetId,
        widget_title: widget.title,
        widget_type: widget.type
      }
    }

    startFocusedSession('widget', widgetId, focusContext, `Tell me more about ${widget.title}`)
  }

  if (showCompact) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
          activeContextSync 
            ? 'bg-synrgy-accent/20 text-synrgy-accent' 
            : 'bg-synrgy-muted/20 text-synrgy-muted'
        }`}>
          {activeContextSync ? <Zap className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
          Sync {activeContextSync ? 'On' : 'Off'}
        </div>
        
        {focusedSession && (
          <div className="flex items-center gap-1 px-2 py-1 rounded-full text-xs border border-synrgy-primary/30 text-synrgy-accent">
            <Target className="h-3 w-3" />
            {focusedSession.type}: {focusedSession.id.slice(-8)}
          </div>
        )}
        
        <div className="relative">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="p-1 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
          >
            <History className="h-4 w-4" />
          </button>

          <AnimatePresence>
            {showHistory && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowHistory(false)}
                />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute top-full right-0 mt-2 w-96 max-w-[80vw] bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-xl z-50"
                >
                  <ContextHistoryView
                    history={contextHistory}
                    onEntrySelect={setSelectedHistoryEntry}
                    onClear={clearContextHistory}
                  />
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-synrgy-surface border border-synrgy-primary/20 rounded-xl ${className}`}>
      <div className="p-4 border-b border-synrgy-primary/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5" />
            <span className="font-medium text-synrgy-text">Context Bridge</span>
          </div>
          
          <div className="flex items-center gap-2">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={activeContextSync}
                onChange={(e) => {
                  const state = useHybridStore.getState()
                  state.activeContextSync = e.target.checked
                }}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-synrgy-bg-900 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-synrgy-accent"></div>
            </label>
            <button 
              onClick={handleManualSync}
              className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-accent hover:bg-synrgy-accent/10 transition-colors"
            >
              <Zap className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-4 space-y-6">
        {/* Focused Session */}
        {focusedSession && (
          <div className="p-4 border border-synrgy-primary/20 rounded-lg bg-blue-50/5">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-synrgy-text">Focused Session</span>
                <div className="px-2 py-1 text-xs border border-synrgy-primary/30 rounded text-synrgy-accent">
                  {focusedSession.type}: {focusedSession.id}
                </div>
              </div>
              <button
                onClick={endFocusedSession}
                className="p-1 rounded text-synrgy-muted hover:text-synrgy-primary transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            {focusedSession.spawnQuery && (
              <p className="text-sm text-synrgy-muted">
                "{focusedSession.spawnQuery}"
              </p>
            )}
          </div>
        )}

        {/* Context Status */}
        <div className="grid grid-cols-2 gap-4">
          {/* Dashboard Context */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="font-medium text-synrgy-text">Dashboard Context</span>
            </div>
            <div className="flex gap-2">
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <Users className="h-3 w-3" />
                {dashboardSummary.entities} entities
              </div>
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <Filter className="h-3 w-3" />
                {dashboardSummary.filters} filters
              </div>
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <MessageCircle className="h-3 w-3" />
                {dashboardSummary.messages} msgs
              </div>
            </div>
            <button
              onClick={handleBridgeFromDashboard}
              disabled={!dashboardContext}
              className="w-full px-3 py-2 text-sm border border-synrgy-primary/20 rounded-lg text-synrgy-text hover:bg-synrgy-primary/10 hover:border-synrgy-primary/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Bridge to Chat →
            </button>
          </div>

          {/* Chat Context */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              <span className="font-medium text-synrgy-text">Chat Context</span>
            </div>
            <div className="flex gap-2">
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <Users className="h-3 w-3" />
                {chatSummary.entities} entities
              </div>
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <Filter className="h-3 w-3" />
                {chatSummary.filters} filters
              </div>
              <div className="flex items-center gap-1 px-2 py-1 text-xs border border-synrgy-primary/20 rounded text-synrgy-muted">
                <MessageCircle className="h-3 w-3" />
                {chatSummary.messages} msgs
              </div>
            </div>
            <button
              onClick={handleBridgeFromChat}
              disabled={!chatContext}
              className="w-full px-3 py-2 text-sm border border-synrgy-primary/20 rounded-lg text-synrgy-text hover:bg-synrgy-primary/10 hover:border-synrgy-primary/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              ← Bridge to Dashboard
            </button>
          </div>
        </div>

        <div className="border-t border-synrgy-primary/10" />

        {/* Widget Focus Spawning */}
        {pinnedWidgets.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4" />
              <span className="font-medium text-synrgy-text">Spawn Focused Chat</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {pinnedWidgets.slice(0, 6).map((widget) => (
                <button
                  key={widget.id}
                  onClick={() => handleSpawnFocusedChat(widget.id)}
                  className="flex items-center gap-2 px-3 py-2 text-sm border border-synrgy-primary/20 rounded-lg text-synrgy-text hover:bg-synrgy-primary/10 hover:border-synrgy-primary/40 transition-all text-left"
                >
                  <Target className="h-3 w-3 flex-shrink-0" />
                  <span className="truncate">{widget.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-synrgy-primary/10" />

        {/* Context History */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4" />
            <span className="font-medium text-synrgy-text">Recent Activity</span>
            <div className="px-2 py-0.5 text-xs bg-synrgy-primary/20 text-synrgy-accent rounded">
              {contextHistory.length}
            </div>
          </div>
          <button
            onClick={() => setShowHistory(true)}
            className="text-sm text-synrgy-muted hover:text-synrgy-primary transition-colors"
          >
            View All
          </button>
        </div>

        <div className="h-32 overflow-y-auto">
          <div className="space-y-2">
            {contextHistory.slice(-5).reverse().map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between p-2 border border-synrgy-primary/10 rounded text-sm"
              >
                <div className="flex items-center gap-2">
                  <div className={`px-2 py-0.5 text-xs rounded ${
                    entry.type === 'sync' ? 'bg-synrgy-accent/20 text-synrgy-accent' :
                    entry.type === 'bridge' ? 'bg-blue-500/20 text-blue-400' : 
                    'bg-synrgy-primary/20 text-synrgy-primary'
                  }`}>
                    {entry.type}
                  </div>
                  <span className="text-synrgy-muted">{entry.from} → {entry.to}</span>
                </div>
                <div className="flex items-center gap-1 text-synrgy-muted">
                  <Clock className="h-3 w-3" />
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* History Dialog */}
      <AnimatePresence>
        {showHistory && (
          <>
            <div
              className="fixed inset-0 z-40 bg-black/50"
              onClick={() => setShowHistory(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 z-50 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-xl max-w-4xl mx-auto"
            >
              <div className="p-4 border-b border-synrgy-primary/10">
                <h3 className="text-lg font-semibold text-synrgy-text">Context Synchronization History</h3>
              </div>
              <ContextHistoryView
                history={contextHistory}
                onEntrySelect={setSelectedHistoryEntry}
                onClear={clearContextHistory}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// Context History View Component
interface ContextHistoryViewProps {
  history: Array<{
    id: string
    type: 'sync' | 'bridge' | 'spawn'
    from: 'dashboard' | 'chat'
    to: 'dashboard' | 'chat'
    context: ConversationContext
    timestamp: string
  }>
  onEntrySelect: (entryId: string) => void
  onClear: () => void
}

const ContextHistoryView: React.FC<ContextHistoryViewProps> = ({
  history,
  onEntrySelect,
  onClear
}) => {
  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-synrgy-muted">
          {history.length} synchronization events
        </span>
        <button 
          onClick={onClear}
          className="px-3 py-1 text-sm border border-synrgy-primary/20 rounded text-synrgy-text hover:bg-synrgy-primary/10 transition-colors"
        >
          Clear History
        </button>
      </div>

      <div className="h-96 overflow-y-auto">
        <div className="space-y-2">
          {history.reverse().map((entry) => (
            <div
              key={entry.id}
              className="cursor-pointer hover:bg-synrgy-primary/10 transition-colors border border-synrgy-primary/10 rounded-lg p-4"
              onClick={() => onEntrySelect(entry.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`px-2 py-0.5 text-xs rounded ${
                    entry.type === 'sync' ? 'bg-synrgy-accent/20 text-synrgy-accent' :
                    entry.type === 'bridge' ? 'bg-blue-500/20 text-blue-400' : 
                    'bg-synrgy-primary/20 text-synrgy-primary'
                  }`}>
                    {entry.type}
                  </div>
                  <ArrowLeftRight className="h-4 w-4 text-synrgy-muted" />
                  <span className="font-mono text-sm text-synrgy-text">
                    {entry.from} → {entry.to}
                  </span>
                </div>
                <span className="text-xs text-synrgy-muted">
                  {new Date(entry.timestamp).toLocaleString()}
                </span>
              </div>
              
              <div className="flex gap-4 text-xs text-synrgy-muted">
                <span>Entities: {Object.keys(entry.context.entities || {}).length}</span>
                <span>Filters: {(entry.context.filters || []).length}</span>
                <span>Messages: {(entry.context.history || []).length}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ContextBridge
