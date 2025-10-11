import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, MoreHorizontal, Trash2, Download, Eye, Wifi, WifiOff, ArrowDown } from 'lucide-react'

import MessageBubble from './MessageBubble'
import Composer from './Composer'
import { useChatStore, useCurrentMessages } from '@/stores/chatStore'
import { useWebSocket, useStreamingChat } from '../../hooks/useWebSocket'
import { ChatMessage } from '../../types'

interface ChatWindowProps {
  className?: string
  showHeader?: boolean
  title?: string
  onSettingsClick?: () => void
}

export default function ChatWindow({ 
  className = '', 
  showHeader = true, 
  title = "SYNRGY Assistant",
  onSettingsClick 
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const lastMessageCountRef = useRef(0)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [hasNewMessages, setHasNewMessages] = useState(false)
  const { 
    clearMessages, 
    toggleExplainQuery, 
    showExplainQuery,
    context,
    currentConversationId,
    error,
    clearError,
    addMessage
  } = useChatStore()
  
  const messages = useCurrentMessages()

  // WebSocket integration
  const { isConnected, isReconnecting, reconnectAttempts, connectionState } = useWebSocket({
    autoConnect: true,
    onChatMessage: (message: ChatMessage) => {
      // Add received message to chat store
      addMessage(message)
    },
    onConnect: () => {
      console.log('WebSocket connected in ChatWindow')
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected in ChatWindow')
    },
    onError: (error) => {
      console.error('WebSocket error in ChatWindow:', error)
    }
  })

  const { streamingMessage, isStreaming } = useStreamingChat()

  // Smart auto-scroll: only scroll if user is near bottom or it's a new message
  useEffect(() => {
    if (messages.length > lastMessageCountRef.current) {
      // New message added
      const container = messagesContainerRef.current
      if (container) {
        const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100
        if (isNearBottom || lastMessageCountRef.current === 0) {
          // Only auto-scroll if user is near bottom or it's the first message
          scrollToBottom('smooth')
          setHasNewMessages(false)
        } else {
          // User is scrolled up, mark as having new messages
          setHasNewMessages(true)
        }
      }
    }
    lastMessageCountRef.current = messages.length
  }, [messages])

  const scrollToBottom = (behavior: ScrollBehavior = 'instant') => {
    messagesEndRef.current?.scrollIntoView({ behavior })
  }

  // Handle scroll events to show/hide scroll button
  useEffect(() => {
    const container = messagesContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100
      setShowScrollButton(!isNearBottom && messages.length > 0)
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [messages.length])

  const handleExportChat = () => {
    // TODO: Implement chat export functionality
    const chatData = {
      conversation_id: currentConversationId,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        metadata: msg.metadata
      })),
      context,
      exported_at: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `synrgy-chat-${currentConversationId || 'export'}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className={`flex flex-col h-full bg-synrgy-bg-900 overflow-hidden ${className}`}>
      {/* Header */}
{showHeader && (
        <div className="sticky top-0 z-10 border-b border-synrgy-primary/10 bg-synrgy-bg-900/80 backdrop-blur-xs">
          <div className="mx-auto w-full max-w-3xl flex items-center justify-between px-4 sm:px-6 md:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-synrgy-primary/20 to-synrgy-accent/20 border border-synrgy-primary/30 rounded-full flex items-center justify-center">
                <span className="text-synrgy-primary font-bold">S</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-synrgy-text">{title}</h1>
                <p className="text-sm text-synrgy-muted">
                  {context?.conversation_id ? `Conversation ${context.conversation_id.slice(0, 8)}...` : 'New conversation'}
                </p>
              </div>
            </div>
          </div>

          {/* Header Actions */}
          <div className="flex items-center gap-2">
            {/* Explain Query Toggle */}
            <button
              onClick={toggleExplainQuery}
              className={`p-2 rounded-lg transition-all ${
                showExplainQuery
                  ? 'bg-synrgy-accent/20 text-synrgy-accent'
                  : 'hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary'
              }`}
              title={showExplainQuery ? 'Hide query explanations' : 'Show query explanations'}
            >
              <Eye className="w-5 h-5" />
            </button>

            {/* Export Chat */}
            {messages.length > 0 && (
              <button
                onClick={handleExportChat}
                className="p-2 hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary rounded-lg transition-colors"
                title="Export conversation"
              >
                <Download className="w-5 h-5" />
              </button>
            )}

            {/* Clear Chat */}
            {messages.length > 0 && (
              <button
                onClick={clearMessages}
                className="p-2 hover:bg-red-500/10 text-synrgy-muted hover:text-red-500 rounded-lg transition-colors"
                title="Clear conversation"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}

            {/* Settings */}
            {onSettingsClick && (
              <button
                onClick={onSettingsClick}
                className="p-2 hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary rounded-lg transition-colors"
                title="Chat settings"
              >
                <Settings className="w-5 h-5" />
              </button>
            )}

            {/* More Options */}
            <button
              className="p-2 hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary rounded-lg transition-colors"
              title="More options"
            >
              <MoreHorizontal className="w-5 h-5" />
            </button>
          </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-500/10 border-b border-red-500/20 px-6 py-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-red-400">
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-sm">{error}</span>
              </div>
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Dismiss
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages Area - Scrollable, fills remaining space */}
      <div className="flex-1 overflow-y-auto">
        <div ref={messagesContainerRef} className="px-4 sm:px-6 md:px-8 py-6 mx-auto w-full max-w-3xl">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center max-w-md mx-auto"
              >
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-synrgy-primary/20 to-synrgy-accent/20 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold text-synrgy-primary">S</span>
                </div>
                
                <h2 className="text-xl font-semibold text-synrgy-text mb-3">
                  Welcome to SYNRGY
                </h2>
                
                <p className="text-synrgy-muted mb-6 leading-relaxed">
                  I'm your conversational SIEM assistant. Ask me anything about your security data, 
                  generate reports, or investigate threats using natural language.
                </p>

                <div className="grid grid-cols-1 gap-3 text-sm">
                  <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-lg p-4 text-left">
                    <div className="font-medium text-synrgy-primary mb-1">Try asking:</div>
                    <div className="text-synrgy-muted">
                      "Show me failed login attempts in the last hour"
                    </div>
                  </div>
                  
                  <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-lg p-4 text-left">
                    <div className="font-medium text-synrgy-primary mb-1">Generate reports:</div>
                    <div className="text-synrgy-muted">
                      "Create a security summary for last week with charts"
                    </div>
                  </div>
                  
                  <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-lg p-4 text-left">
                    <div className="font-medium text-synrgy-primary mb-1">Investigate threats:</div>
                    <div className="text-synrgy-muted">
                      "What are the top threat indicators today?"
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          ) : (
            <div className="space-y-1">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    isLatest={index === messages.length - 1}
                  />
                ))}
              </AnimatePresence>
              
              {/* Scroll anchor */}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Floating Scroll to Bottom Button */}
        <AnimatePresence>
          {showScrollButton && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={() => {
                scrollToBottom('smooth')
                setHasNewMessages(false)
              }}
              className="absolute bottom-24 right-6 w-10 h-10 bg-synrgy-primary hover:bg-synrgy-primary/90 text-synrgy-bg-900 rounded-full shadow-lg hover:shadow-synrgy-glow/50 transition-all duration-200 flex items-center justify-center z-10"
              title={hasNewMessages ? 'New messages - scroll to bottom' : 'Scroll to bottom'}
            >
              <ArrowDown className="w-5 h-5" />
              {hasNewMessages && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-synrgy-accent rounded-full animate-pulse" />
              )}
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Composer (sticky like ChatGPT) */}
      <div className="sticky bottom-0 border-t border-synrgy-primary/10 bg-synrgy-bg-900/90 backdrop-blur-xs">
        <div className="mx-auto w-full max-w-3xl px-4 sm:px-6 md:px-8 py-4">
          <Composer
            disabled={false}
            placeholder={
              messages.length === 0 
                ? "Ask SYNRGY anything about your security data..." 
                : "Continue the conversation..."
            }
          />
          <div className="mt-2 flex items-center justify-between text-[11px] text-synrgy-muted">
            <span>Press Enter to send • Shift + Enter for new line • Esc to close suggestions</span>
            <span className="hidden sm:inline">Model: SYNRGY Pipeline</span>
          </div>
        </div>
      </div>
    </div>
  )
}
