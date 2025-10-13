/**
 * SYNRGY Enhanced HybridLayout - Dashboard + Chat Integration
 * Implements the SYNRGY.TXT hybrid mode with two-way sync
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageCircle,
  LayoutGrid,
  Maximize2,
  Minimize2,
  X,
  Send,
  Bot,
  ExternalLink,
  Pin,
} from 'lucide-react'

import DashboardGrid from '@/components/Dashboard/DashboardGrid'
import ChatWindow from '@/components/Chat/ChatWindow'
import { useChatStore } from '@/stores/chatStore'
import { useAppStore } from '@/stores/appStore'
import type { DashboardWidget } from '@/types'

interface HybridLayoutProps {
  className?: string
}

interface WidgetContext {
  id: string
  type: string
  title: string
  timeRange?: {
    start: string
    end: string
  }
  filters?: Record<string, any>
  clickedRegion?: {
    x: number
    y: number
    data: any
  }
  metadata?: Record<string, any>
}

export default function EnhancedHybridLayout({ className = '' }: HybridLayoutProps) {
  const [chatPanelExpanded, setChatPanelExpanded] = useState(false)
  const [contextMessage, setContextMessage] = useState<string>('')
  const [widgetContext, setWidgetContext] = useState<WidgetContext | null>(null)
  const [isProcessingContext, setIsProcessingContext] = useState(false)

  const chatInputRef = useRef<HTMLInputElement>(null)

  const { sendMessage, isLoading, currentConversationId } = useChatStore()
  const { setChatPanelOpen } = useAppStore()

  // Handle widget click events from dashboard
  const handleWidgetClick = useCallback(
    (widget: DashboardWidget, clickData?: any) => {
      const context: WidgetContext = {
        id: widget.id,
        type: widget.type,
        title: widget.title,
        clickedRegion: clickData,
        metadata: widget.config || {},
      }

      setWidgetContext(context)

      // Generate contextual message based on widget type and click
      let message = ''
      switch (widget.type) {
        case 'chart':
          message = clickData
            ? `Investigate the spike in ${widget.title} at ${clickData.x || 'this time period'}. Show me the underlying security events.`
            : `Analyze the data shown in ${widget.title}. What security patterns do you see?`
          break
        case 'summary_card':
          message = `Explain the ${widget.title} metric and investigate any anomalies. Provide recommendations.`
          break
        case 'table':
          message = `Investigate the security events shown in ${widget.title}. Focus on high-priority items.`
          break
        default:
          message = `Analyze the ${widget.title} widget. What insights can you provide about the security data?`
      }

      setContextMessage(message)
      setChatPanelExpanded(true)
      setChatPanelOpen(true)

      // Focus input after animation
      setTimeout(() => {
        chatInputRef.current?.focus()
      }, 300)
    },
    [setChatPanelOpen]
  )

  // Handle chat panel expand/collapse
  const toggleChatPanel = useCallback(() => {
    setChatPanelExpanded(prev => !prev)
    setChatPanelOpen(!chatPanelExpanded)
  }, [chatPanelExpanded, setChatPanelOpen])

  // Send contextual message
  const handleSendContext = useCallback(async () => {
    if (!contextMessage.trim()) return

    setIsProcessingContext(true)

    try {
      await sendMessage({
        query: contextMessage,
        conversation_id: currentConversationId || undefined,
        user_context: widgetContext
          ? {
              widget_context: widgetContext,
              source: 'dashboard_widget',
            }
          : undefined,
      })

      // Clear context after sending
      setContextMessage('')
      setWidgetContext(null)
    } catch (error) {
      console.error('Failed to send contextual message:', error)
    } finally {
      setIsProcessingContext(false)
    }
  }, [contextMessage, sendMessage, currentConversationId, widgetContext])

  // Handle pinning chat results to dashboard
  const handlePinToDashboard = useCallback((visual: any) => {
    console.log('Pin to dashboard:', visual)

    // Create new dashboard widget from visual data
    const newWidget: Partial<DashboardWidget> = {
      id: `pinned_${Date.now()}`,
      type: visual.type === 'summary_card' ? 'summary_card' : 'chart',
      title: visual.title || 'Pinned from Chat',
      data: visual.data,
      config: {
        ...visual.config,
        pinned_from_chat: true,
        original_visual: visual,
      },
      position: {
        row: 0,
        col: 0,
        width: visual.type === 'summary_card' ? 1 : 2,
        height: visual.type === 'summary_card' ? 1 : 2,
      },
    }

    // TODO: Add to dashboard widget store
    console.log('New pinned widget:', newWidget)

    // Show success feedback
    // Could use toast notification here
  }, [])

  // Handle export functionality
  const handleExport = useCallback((visual: any) => {
    console.log('Export visual:', visual)

    // TODO: Implement export functionality
    // Could generate CSV, PNG, or PDF based on visual type

    // For now, just download JSON
    const dataStr = JSON.stringify(visual, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${visual.title || 'visual'}_export.json`
    link.click()
    URL.revokeObjectURL(url)
  }, [])

  return (
    <div className={`h-screen bg-synrgy-bg-900 flex ${className}`}>
      {/* Dashboard Panel */}
      <motion.div
        initial={false}
        animate={{
          width: chatPanelExpanded ? '60%' : '100%',
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="flex flex-col border-r border-synrgy-primary/10 bg-synrgy-bg-900"
      >
        {/* Dashboard Header */}
        <div className="flex items-center justify-between p-4 border-b border-synrgy-primary/10 bg-synrgy-surface/30">
          <div className="flex items-center gap-3">
            <LayoutGrid className="w-5 h-5 text-synrgy-primary" />
            <h1 className="text-lg font-heading font-bold text-synrgy-text">
              ＳＹＮＲＧＹ Dashboard
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleChatPanel}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 ${
                chatPanelExpanded
                  ? 'bg-synrgy-primary text-synrgy-bg-900'
                  : 'bg-synrgy-primary/20 text-synrgy-primary hover:bg-synrgy-primary/30'
              }`}
            >
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm font-medium">
                {chatPanelExpanded ? 'Hide Chat' : 'Ask CYNRGY'}
              </span>
            </button>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto">
          <DashboardGrid onWidgetClick={handleWidgetClick} interactive={true} />
        </div>
      </motion.div>

      {/* Chat Panel */}
      <AnimatePresence>
        {chatPanelExpanded && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: '40%', opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="flex flex-col bg-synrgy-surface border-l border-synrgy-primary/20"
          >
            {/* Chat Header */}
            <div className="flex items-center justify-between p-4 border-b border-synrgy-primary/10 bg-synrgy-bg-900/50">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-synrgy-primary/20 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-synrgy-primary" />
                </div>
                <div>
                  <h2 className="font-medium text-synrgy-text">CYNRGY Assistant</h2>
                  <p className="text-xs text-synrgy-muted">
                    {widgetContext ? `Investigating: ${widgetContext.title}` : 'Ready to analyze'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => setChatPanelExpanded(false)}
                  className="p-2 hover:bg-synrgy-primary/20 rounded transition-colors"
                  title="Minimize"
                >
                  <Minimize2 className="w-4 h-4 text-synrgy-muted" />
                </button>
                <button
                  onClick={toggleChatPanel}
                  className="p-2 hover:bg-synrgy-primary/20 rounded transition-colors"
                  title="Close"
                >
                  <X className="w-4 h-4 text-synrgy-muted" />
                </button>
              </div>
            </div>

            {/* Context Message Input */}
            {contextMessage && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-4 bg-synrgy-primary/5 border-b border-synrgy-primary/10"
              >
                <div className="text-xs text-synrgy-accent mb-2 flex items-center gap-2">
                  <ExternalLink className="w-3 h-3" />
                  Context from dashboard widget
                </div>
                <div className="flex gap-2">
                  <input
                    ref={chatInputRef}
                    value={contextMessage}
                    onChange={e => setContextMessage(e.target.value)}
                    className="flex-1 px-3 py-2 bg-synrgy-bg-900/50 border border-synrgy-primary/20 
                             rounded text-synrgy-text text-sm focus:border-synrgy-primary/40 focus:outline-none"
                    placeholder="Edit or confirm the investigation query..."
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendContext()
                      }
                    }}
                  />
                  <button
                    onClick={handleSendContext}
                    disabled={isProcessingContext || isLoading}
                    className="px-3 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded 
                             hover:bg-synrgy-primary/90 disabled:opacity-50 transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            )}

            {/* Chat Window */}
            <div className="flex-1 flex flex-col">
              <ChatWindow
                className="flex-1"
                onPin={handlePinToDashboard}
                onExport={handleExport}
                compact={true}
                showHeader={false}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Chat Button (when panel is closed) */}
      <AnimatePresence>
        {!chatPanelExpanded && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={toggleChatPanel}
            className="fixed bottom-6 right-6 w-14 h-14 bg-synrgy-primary hover:bg-synrgy-primary/90 
                     text-synrgy-bg-900 rounded-full shadow-lg z-50 flex items-center justify-center
                     transition-all duration-200 hover:scale-110"
          >
            <MessageCircle className="w-6 h-6" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}
