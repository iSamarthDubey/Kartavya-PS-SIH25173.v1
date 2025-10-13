/**
 * Smart Context Trigger - Intelligent context-aware chat spawning
 */

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageCircle,
  Sparkles,
  Target,
  Brain,
  Lightbulb,
  TrendingUp,
  AlertCircle,
  Search,
  Send,
  History,
  BookOpen,
  Zap,
} from 'lucide-react'
import { useHybridStore, useContextSync } from '../../stores/hybridStore'
import type { DashboardWidget, ConversationContext } from '../../types'

interface SmartContextTriggerProps {
  widget: DashboardWidget
  className?: string
  variant?: 'button' | 'icon' | 'minimal'
  onSpawn?: (context: ConversationContext, query: string) => void
}

export const SmartContextTrigger: React.FC<SmartContextTriggerProps> = ({
  widget,
  className = '',
  variant = 'icon',
  onSpawn,
}) => {
  const { startFocusedSession, bridgeContext } = useContextSync()
  const [isOpen, setIsOpen] = useState(false)
  const [customQuery, setCustomQuery] = useState('')
  const [selectedIntent, setSelectedIntent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Smart query suggestions based on widget type and data
  const generateSmartQueries = (
    widget: DashboardWidget
  ): Array<{
    intent: string
    query: string
    icon: React.ElementType
    category: 'analysis' | 'insight' | 'action'
  }> => {
    const baseQueries = []

    switch (widget.type) {
      case 'chart':
        baseQueries.push(
          {
            intent: 'trend_analysis',
            query: `Analyze the trends shown in "${widget.title}" and explain what's driving these patterns`,
            icon: TrendingUp,
            category: 'analysis' as const,
          },
          {
            intent: 'forecast',
            query: `Based on "${widget.title}", what can we expect in the coming period?`,
            icon: Brain,
            category: 'insight' as const,
          },
          {
            intent: 'correlation',
            query: `What factors are correlated with the metrics in "${widget.title}"?`,
            icon: Sparkles,
            category: 'insight' as const,
          }
        )
        break

      case 'table':
        baseQueries.push(
          {
            intent: 'deep_dive',
            query: `Provide detailed insights on the data shown in "${widget.title}" table`,
            icon: Search,
            category: 'analysis' as const,
          },
          {
            intent: 'outliers',
            query: `Identify and explain any outliers or anomalies in "${widget.title}"`,
            icon: AlertCircle,
            category: 'insight' as const,
          }
        )
        break

      case 'summary_card':
        baseQueries.push(
          {
            intent: 'context',
            query: `Provide context and background for the "${widget.title}" metric`,
            icon: BookOpen,
            category: 'analysis' as const,
          },
          {
            intent: 'improvement',
            query: `How can we improve the "${widget.title}" metric? What are the key levers?`,
            icon: Lightbulb,
            category: 'action' as const,
          }
        )
        break

      default:
        baseQueries.push({
          intent: 'explain',
          query: `Explain the "${widget.title}" widget and its significance`,
          icon: BookOpen,
          category: 'analysis' as const,
        })
    }

    // Add common queries for all widget types
    baseQueries.push(
      {
        intent: 'actionable',
        query: `What actionable insights can you derive from "${widget.title}"?`,
        icon: Zap,
        category: 'action' as const,
      },
      {
        intent: 'comparison',
        query: `How does "${widget.title}" compare to industry benchmarks or historical data?`,
        icon: TrendingUp,
        category: 'insight' as const,
      }
    )

    return baseQueries
  }

  const smartQueries = generateSmartQueries(widget)

  const handleSpawnChat = async (query: string, intent?: string) => {
    setIsLoading(true)

    try {
      // Create rich context from widget data
      const focusContext: ConversationContext = {
        conversation_id: `smart_focus_${widget.id}_${Date.now()}`,
        history: [],
        entities: {
          widget_id: widget.id,
          widget_title: widget.title,
          widget_type: widget.type,
          intent: intent || 'custom',
        },
        filters: [],
        time_range: widget.data?.time_range || undefined,
        metadata: {
          focused_widget: widget.id,
          widget_title: widget.title,
          widget_type: widget.type,
          widget_data: widget.data,
          widget_config: widget.config,
          spawn_intent: intent,
          spawn_timestamp: new Date().toISOString(),
          smart_trigger: true,
        },
      }

      // Start focused session
      startFocusedSession('widget', widget.id, focusContext, query)

      // Bridge widget context to chat
      bridgeContext('dashboard', focusContext)

      // Notify parent component
      onSpawn?.(focusContext, query)

      // Close popover
      setIsOpen(false)
      setCustomQuery('')
      setSelectedIntent('')
    } catch (error) {
      console.error('Failed to spawn focused chat:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickSpawn = (query: string, intent: string) => {
    handleSpawnChat(query, intent)
  }

  const handleCustomSpawn = () => {
    if (!customQuery.trim()) return
    handleSpawnChat(customQuery, selectedIntent || 'custom')
  }

  // Auto-focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  const renderTrigger = () => {
    switch (variant) {
      case 'button':
        return (
          <button
            className={`px-3 py-2 border border-synrgy-primary/20 rounded-lg text-sm font-medium text-synrgy-text hover:bg-synrgy-primary/10 hover:border-synrgy-primary/40 transition-all ${className}`}
          >
            <MessageCircle className="h-4 w-4 mr-2 inline" />
            Ask SYNRGY
          </button>
        )
      case 'minimal':
        return (
          <button
            className={`p-1 h-7 w-7 rounded-lg text-synrgy-accent hover:bg-synrgy-accent/10 transition-colors ${className}`}
          >
            <MessageCircle className="h-3 w-3" />
          </button>
        )
      default:
        return (
          <button
            className={`p-2 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors ${className}`}
          >
            <MessageCircle className="h-4 w-4" />
          </button>
        )
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'analysis':
        return 'border-blue-500/30 text-blue-400'
      case 'insight':
        return 'border-green-500/30 text-green-400'
      case 'action':
        return 'border-orange-500/30 text-orange-400'
      default:
        return 'border-synrgy-primary/30 text-synrgy-accent'
    }
  }

  return (
    <div className="relative">
      <div title="Spawn focused chat session for this widget" onClick={() => setIsOpen(!isOpen)}>
        {renderTrigger()}
      </div>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

            {/* Popover */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="absolute top-full left-0 mt-2 w-96 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-xl z-50"
            >
              <div className="p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="h-5 w-5 text-blue-600" />
                  <div>
                    <h4 className="font-medium text-synrgy-text">Focus Chat on</h4>
                    <p className="text-sm text-synrgy-muted">{widget.title}</p>
                  </div>
                </div>

                {/* Smart Query Suggestions */}
                <div className="space-y-3 mb-4">
                  <h5 className="text-sm font-medium flex items-center gap-1 text-synrgy-text">
                    <Sparkles className="h-4 w-4" />
                    Smart Suggestions
                  </h5>

                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {smartQueries.map(suggestion => {
                      const IconComponent = suggestion.icon
                      return (
                        <div
                          key={suggestion.intent}
                          className="cursor-pointer hover:bg-synrgy-primary/10 transition-colors border border-synrgy-primary/10 rounded-lg p-3"
                          onClick={() => handleQuickSpawn(suggestion.query, suggestion.intent)}
                        >
                          <div className="flex items-start gap-2">
                            <IconComponent className="h-4 w-4 mt-0.5 text-blue-600 flex-shrink-0" />
                            <div className="flex-1">
                              <p className="text-sm font-medium mb-1 capitalize text-synrgy-text">
                                {suggestion.intent.replace('_', ' ')}
                              </p>
                              <p className="text-xs text-synrgy-muted">{suggestion.query}</p>
                              <div
                                className={`inline-block mt-2 px-2 py-0.5 text-xs border rounded-full ${getCategoryColor(suggestion.category)}`}
                              >
                                {suggestion.category}
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="border-t border-synrgy-primary/10 my-4" />

                {/* Custom Query */}
                <div className="space-y-3">
                  <h5 className="text-sm font-medium flex items-center gap-1 text-synrgy-text">
                    <Brain className="h-4 w-4" />
                    Custom Query
                  </h5>

                  <div className="space-y-2">
                    <select
                      value={selectedIntent}
                      onChange={e => setSelectedIntent(e.target.value)}
                      className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:border-synrgy-primary/50 outline-none"
                    >
                      <option value="">Select intent (optional)</option>
                      <option value="analysis">Analysis</option>
                      <option value="insight">Insight</option>
                      <option value="action">Action</option>
                      <option value="comparison">Comparison</option>
                      <option value="forecast">Forecast</option>
                      <option value="custom">Custom</option>
                    </select>

                    <textarea
                      ref={inputRef}
                      value={customQuery}
                      onChange={e => setCustomQuery(e.target.value)}
                      placeholder={`Ask about "${widget.title}"...`}
                      className="w-full min-h-[80px] px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg text-synrgy-text placeholder:text-synrgy-muted resize-none focus:border-synrgy-primary/50 outline-none"
                      onKeyDown={e => {
                        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                          handleCustomSpawn()
                        }
                      }}
                    />

                    <div className="flex justify-between items-center">
                      <p className="text-xs text-synrgy-muted">Ctrl+Enter to send</p>
                      <button
                        onClick={handleCustomSpawn}
                        disabled={!customQuery.trim() || isLoading}
                        className="px-4 py-2 bg-synrgy-accent text-synrgy-bg-900 rounded-lg font-medium hover:bg-synrgy-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm flex items-center gap-2"
                      >
                        {isLoading ? (
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 border border-current border-r-transparent rounded-full animate-spin" />
                            Spawning...
                          </div>
                        ) : (
                          <>
                            <Send className="h-3 w-3" />
                            Spawn Chat
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default SmartContextTrigger
