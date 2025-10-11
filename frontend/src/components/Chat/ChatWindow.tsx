import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, MoreHorizontal, Trash2, Download, Eye, Wifi, WifiOff } from 'lucide-react'

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

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

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
    <div className={`flex flex-col h-full bg-synrgy-bg-900 ${className}`}>
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10">
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

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto px-6 py-6">
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
      </div>

      {/* Composer */}
      <div className="border-t border-synrgy-primary/10 p-6">
        <Composer
          disabled={false}
          placeholder={
            messages.length === 0 
              ? "Ask SYNRGY anything about your security data..." 
              : "Continue the conversation..."
          }
        />
      </div>

      {/* Connection Status */}
      <div className="flex items-center justify-center py-2 text-xs text-synrgy-muted border-t border-synrgy-primary/5">
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <Wifi className="w-3 h-3" />
              <span>Connected to SYNRGY</span>
            </>
          ) : isReconnecting ? (
            <>
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span>Reconnecting... (attempt {reconnectAttempts})</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <WifiOff className="w-3 h-3" />
              <span>Disconnected</span>
            </>
          )}
          
          {context?.conversation_id && (
            <>
              <span>•</span>
              <span>{messages.length} messages</span>
            </>
          )}
          
          {isStreaming && (
            <>
              <span>•</span>
              <span className="text-synrgy-accent animate-pulse">Streaming...</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
