import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send,
  Mic,
  MicOff,
  Paperclip,
  Zap,
  Clock,
  Shield,
  BarChart3,
  AlertTriangle
} from 'lucide-react'
import { useChatStore } from '@/stores/chatStore'
import { useQuery } from '@tanstack/react-query'
import { chatApi } from '@/services/api'
import { useWebSocket, useStreamingChat } from '@/hooks/useWebSocket'

interface ComposerProps {
  className?: string
  disabled?: boolean
  placeholder?: string
}

const QUICK_SUGGESTIONS = [
  {
    icon: Shield,
    text: "Show me failed login attempts in the last hour",
    category: "Security"
  },
  {
    icon: BarChart3,
    text: "What are the top threat indicators today?",
    category: "Analytics"
  },
  {
    icon: AlertTriangle,
    text: "Any critical alerts I should know about?",
    category: "Alerts"
  },
  {
    icon: Clock,
    text: "Generate security summary for last week",
    category: "Reports"
  }
]

export default function Composer({ className = '', disabled = false, placeholder = "Ask ＳＹＮＲＧＹ anything..." }: ComposerProps) {
  const [message, setMessage] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { sendMessage, isLoading, context, suggestions } = useChatStore()
  
  // WebSocket for real-time features (but keep it simple)
  const { isConnected } = useWebSocket({
    autoConnect: true,
    onConnect: () => console.log('WebSocket connected for real-time updates'),
    onDisconnect: () => console.log('WebSocket disconnected, using HTTP mode')
  })
  
  // Streaming chat capabilities
  const { } = useStreamingChat()

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [message])

  // Focus on textarea when not loading
  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [isLoading])

  // Get suggestions from backend
  const { data: backendSuggestions } = useQuery({
    queryKey: ['chat-suggestions'],
    queryFn: chatApi.getSuggestions,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isLoading || disabled) return

    const queryText = message.trim()
    
    // Clear input immediately
    setMessage('')
    setShowSuggestions(false)
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    try {
      // Let sendMessage handle everything - don't add user message here
      await sendMessage({
        query: queryText,
        conversation_id: context?.conversation_id || 'new_conversation'
      })
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }

    if (e.key === 'Escape') {
      setShowSuggestions(false)
    }

    // Show suggestions on focus or typing
    if (e.key !== 'Escape' && e.key !== 'Enter') {
      setShowSuggestions(true)
    }
  }

  const handleSuggestionClick = (suggestionText: string) => {
    setMessage(suggestionText)
    setShowSuggestions(false)
    // Focus back to textarea
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus()
        textareaRef.current.setSelectionRange(suggestionText.length, suggestionText.length)
      }
    }, 100)
  }

  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false)
      // TODO: Implement speech-to-text
    } else {
      // Start recording
      setIsRecording(true)
      // TODO: Implement speech-to-text
    }
  }

  const contextSuggestions = suggestions || []
  const allSuggestions = [...QUICK_SUGGESTIONS, ...contextSuggestions.map(s => ({ icon: Zap, text: s, category: "Context" }))]

  return (
    <div className={`relative ${className}`}>
      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showSuggestions && message.length < 3 && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute bottom-full left-0 right-0 mb-2 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-2xl overflow-hidden z-10"
          >
            <div className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-synrgy-accent" />
                <span className="text-sm font-medium text-synrgy-text">Quick Suggestions</span>
              </div>
              
              <div className="grid gap-2 max-h-64 overflow-y-auto">
                {allSuggestions.slice(0, 6).map((suggestion, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                    className="flex items-center gap-3 p-3 text-left hover:bg-synrgy-primary/10 rounded-lg transition-colors group"
                  >
                    <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center group-hover:bg-synrgy-primary/20 transition-colors">
                      <suggestion.icon className="w-4 h-4 text-synrgy-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-synrgy-text line-clamp-1">
                        {suggestion.text}
                      </div>
                      <div className="text-xs text-synrgy-muted">
                        {suggestion.category}
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Additional suggestions from backend */}
              {backendSuggestions?.data?.suggestions && (
                <div className="mt-4 pt-4 border-t border-synrgy-primary/10">
                  <div className="text-xs text-synrgy-muted mb-2">Popular queries</div>
                  <div className="flex flex-wrap gap-2">
                    {backendSuggestions.data.suggestions.slice(0, 2).map((category) =>
                      category.queries.slice(0, 2).map((query, index) => (
                        <button
                          key={`backend-${index}`}
                          onClick={() => handleSuggestionClick(query)}
                          className="text-xs bg-synrgy-primary/10 text-synrgy-primary px-3 py-1 rounded-full hover:bg-synrgy-primary/20 transition-colors"
                        >
                          {query}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Context chips */}
      {context && context.entities && Object.keys(context.entities).length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {Object.entries(context.entities).slice(0, 3).map(([key, values]) => (
            <div
              key={key}
              className="flex items-center gap-2 bg-synrgy-accent/10 text-synrgy-accent px-3 py-1 rounded-full text-xs"
            >
              <span className="font-medium">{key}:</span>
              <span>{Array.isArray(values) ? values[0] : values}</span>
            </div>
          ))}
        </div>
      )}

      {/* Main Composer */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="bg-synrgy-surface border border-synrgy-primary/20 rounded-2xl p-4 focus-within:border-synrgy-primary/50 transition-colors">
          <div className="flex items-start gap-4">
            {/* Text Input */}
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                placeholder={placeholder}
                disabled={disabled || isLoading}
                className="w-full bg-transparent text-synrgy-text placeholder:text-synrgy-muted resize-none outline-none min-h-[24px] max-h-32 overflow-y-auto scrollbar-hide"
                rows={1}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              {/* Voice Input */}
              <button
                type="button"
                onClick={toggleRecording}
                disabled={disabled}
                className={`p-2 rounded-lg transition-all ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'bg-synrgy-primary/10 text-synrgy-primary hover:bg-synrgy-primary/20'
                }`}
                title={isRecording ? 'Stop recording' : 'Voice input'}
              >
                {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>

              {/* Attachments (Future) */}
              <button
                type="button"
                disabled={disabled}
                className="p-2 bg-synrgy-primary/10 text-synrgy-primary hover:bg-synrgy-primary/20 rounded-lg transition-colors opacity-50"
                title="Attachments (coming soon)"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={!message.trim() || isLoading || disabled}
                className={`p-2 rounded-lg transition-all ${
                  !message.trim() || isLoading || disabled
                    ? 'bg-synrgy-muted/20 text-synrgy-muted cursor-not-allowed'
                    : 'bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 hover:scale-105 active:scale-95'
                }`}
                title="Send message"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-synrgy-bg-900 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Character count / status */}
          <div className="flex items-center justify-between mt-2 text-xs text-synrgy-muted">
            <div className="flex items-center gap-4">
              {isLoading && (
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-synrgy-primary rounded-full animate-pulse" />
                  <span>ＳＹＮＲＧＹ is processing...</span>
                </div>
              )}
              
              {!isConnected && (
                <div className="flex items-center gap-2 text-yellow-500">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                  <span>Real-time features offline</span>
                </div>
              )}
              
              {isConnected && (
                <div className="flex items-center gap-2 text-green-500">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span>Real-time connected</span>
                </div>
              )}
              
              {isRecording && (
                <div className="flex items-center gap-2 text-red-500">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span>Recording...</span>
                </div>
              )}
            </div>
            
            <div className="text-right">
              <span className={message.length > 500 ? 'text-synrgy-accent' : ''}>
                {message.length}/1000
              </span>
            </div>
          </div>
        </div>

        {/* Keyboard shortcuts hint */}
        <div className="flex items-center justify-center mt-2 text-xs text-synrgy-muted">
          <span>Press Enter to send • Shift + Enter for new line • Esc to close suggestions</span>
        </div>
      </form>
    </div>
  )
}
