/**
 * SYNRGY Enhanced Chat Interface
 * World-class conversational SIEM assistant with visual-first approach
 */

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Mic, 
  MicOff, 
  Paperclip, 
  Smile, 
  MoreVertical,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Bookmark,
  Share,
  Zap,
  Shield,
  Bot,
  User as UserIcon,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react'

import { 
  AnimatedCard, 
  LoadingSpinner, 
  useToast, 
  TouchButton,
  ResponsiveContainer,
  useBreakpoint 
} from '@/components/UI'
import { VisualRenderer } from '@/components/Chat/VisualRenderer'
import type { ChatMessage, VisualPayload } from '@/types'

interface ChatInterfaceProps {
  messages?: ChatMessage[]
  onSendMessage?: (message: string, attachments?: File[]) => void
  onVoiceInput?: (audioBlob: Blob) => void
  isLoading?: boolean
  isTyping?: boolean
  placeholder?: string
  className?: string
}

interface MessageBubbleProps {
  message: ChatMessage
  isUser: boolean
  onRegenerate?: () => void
  onCopy?: () => void
  onBookmark?: () => void
  onFeedback?: (positive: boolean) => void
}

// Enhanced Message Bubble
const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isUser,
  onRegenerate,
  onCopy,
  onBookmark,
  onFeedback
}) => {
  const [showActions, setShowActions] = useState(false)
  const { showToast } = useToast()
  const { isMobile } = useBreakpoint()

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    showToast({
      type: 'success',
      title: 'Copied!',
      message: 'Message copied to clipboard'
    })
    onCopy?.()
  }

  const handleBookmark = () => {
    showToast({
      type: 'success',
      title: 'Bookmarked',
      message: 'Message saved to bookmarks'
    })
    onBookmark?.()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'} group`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Avatar */}
      {!isUser && (
        <motion.div 
          className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center"
          whileHover={{ scale: 1.1 }}
          transition={{ type: "spring", stiffness: 400 }}
        >
          <Shield className="w-5 h-5 text-synrgy-bg-900" />
        </motion.div>
      )}

      <div className={`flex-1 max-w-4xl ${isUser ? 'flex justify-end' : ''}`}>
        {/* Message Container */}
        <AnimatedCard
          className={`
            relative p-4 ${isUser ? 'ml-12' : 'mr-12'} 
            ${isUser 
              ? 'bg-gradient-to-r from-synrgy-primary to-synrgy-accent text-synrgy-bg-900' 
              : 'bg-synrgy-surface border border-synrgy-primary/20'
            }
          `}
          hoverable={!isMobile}
        >
          {/* Message Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${isUser ? 'text-synrgy-bg-900/80' : 'text-synrgy-primary'}`}>
                {isUser ? 'You' : 'SYNRGY Assistant'}
              </span>
              {message.timestamp && (
                <span className={`text-xs ${isUser ? 'text-synrgy-bg-900/60' : 'text-synrgy-muted'}`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>

            {/* Message Status */}
            {isUser && (
              <div className="flex items-center gap-1">
                {message.status === 'sending' && <Loader2 className="w-3 h-3 animate-spin" />}
                {message.status === 'sent' && <CheckCircle2 className="w-3 h-3" />}
                {message.status === 'error' && <AlertCircle className="w-3 h-3 text-red-400" />}
              </div>
            )}
          </div>

          {/* Message Content */}
          <div className={`${isUser ? 'text-synrgy-bg-900' : 'text-synrgy-text'}`}>
            {/* Text Content */}
            <div className="prose prose-sm max-w-none mb-4">
              {message.content}
            </div>

            {/* Visual Payloads */}
            {message.visual_payloads && message.visual_payloads.length > 0 && (
              <div className="space-y-4">
                {message.visual_payloads.map((payload, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-synrgy-bg-950/50 rounded-xl p-4 border border-synrgy-primary/10"
                  >
                    <VisualRenderer 
                      payload={payload} 
                      className="w-full"
                      compact={isMobile}
                    />
                  </motion.div>
                ))}
              </div>
            )}

            {/* Message Actions */}
            <AnimatePresence>
              {(showActions || isMobile) && !isUser && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="flex items-center gap-2 mt-4 pt-3 border-t border-synrgy-primary/10"
                >
                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={handleCopy}
                    className="text-synrgy-muted hover:text-synrgy-text"
                  >
                    <Copy className="w-4 h-4" />
                  </TouchButton>

                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={handleBookmark}
                    className="text-synrgy-muted hover:text-synrgy-text"
                  >
                    <Bookmark className="w-4 h-4" />
                  </TouchButton>

                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={onRegenerate}
                    className="text-synrgy-muted hover:text-synrgy-text"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </TouchButton>

                  <div className="flex-1" />

                  {/* Feedback Buttons */}
                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={() => onFeedback?.(true)}
                    className="text-synrgy-muted hover:text-green-500"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </TouchButton>

                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={() => onFeedback?.(false)}
                    className="text-synrgy-muted hover:text-red-500"
                  >
                    <ThumbsDown className="w-4 h-4" />
                  </TouchButton>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </AnimatedCard>
      </div>

      {/* User Avatar */}
      {isUser && (
        <motion.div 
          className="flex-shrink-0 w-10 h-10 rounded-full bg-synrgy-surface border-2 border-synrgy-primary/20 flex items-center justify-center"
          whileHover={{ scale: 1.1 }}
          transition={{ type: "spring", stiffness: 400 }}
        >
          <UserIcon className="w-5 h-5 text-synrgy-primary" />
        </motion.div>
      )}
    </motion.div>
  )
}

// Typing Indicator
const TypingIndicator: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: 20 }}
    className="flex gap-4 justify-start"
  >
    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center">
      <Shield className="w-5 h-5 text-synrgy-bg-900" />
    </div>

    <div className="bg-synrgy-surface border border-synrgy-primary/20 rounded-2xl px-6 py-4 mr-12">
      <div className="flex items-center gap-2">
        <span className="text-synrgy-muted text-sm">SYNRGY is thinking</span>
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 bg-synrgy-primary rounded-full"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2
              }}
            />
          ))}
        </div>
      </div>
    </div>
  </motion.div>
)

// Enhanced Message Composer
interface MessageComposerProps {
  onSend: (message: string, attachments?: File[]) => void
  onVoiceInput?: (audioBlob: Blob) => void
  placeholder?: string
  disabled?: boolean
}

const MessageComposer: React.FC<MessageComposerProps> = ({
  onSend,
  onVoiceInput,
  placeholder = "Ask SYNRGY anything about your security data...",
  disabled = false
}) => {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<File[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { isMobile } = useBreakpoint()

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleSend = () => {
    if (!message.trim() && attachments.length === 0) return
    
    onSend(message.trim(), attachments)
    setMessage('')
    setAttachments([])
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileAttachment = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setIsRecording(true)
      // Implementation for voice recording would go here
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = () => {
    setIsRecording(false)
    // Stop recording and call onVoiceInput
  }

  return (
    <div className="border-t border-synrgy-primary/10 bg-synrgy-surface/50 backdrop-blur-sm">
      <ResponsiveContainer padding className="py-4">
        {/* Attachments Preview */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {attachments.map((file, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-2 bg-synrgy-bg-950 rounded-lg px-3 py-2 border border-synrgy-primary/20"
              >
                <Paperclip className="w-4 h-4 text-synrgy-primary" />
                <span className="text-sm text-synrgy-text truncate max-w-[200px]">
                  {file.name}
                </span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-synrgy-muted hover:text-red-400 transition-colors"
                >
                  ×
                </button>
              </motion.div>
            ))}
          </div>
        )}

        {/* Message Input */}
        <div className="flex items-end gap-3">
          {/* Input Container */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder}
              disabled={disabled}
              className={`
                w-full resize-none rounded-2xl px-4 py-3 pr-12
                bg-synrgy-bg-950 border border-synrgy-primary/20
                text-synrgy-text placeholder:text-synrgy-muted
                focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:border-transparent
                ${isMobile ? 'min-h-[48px]' : 'min-h-[44px]'}
                max-h-32 overflow-y-auto
              `}
              rows={1}
            />

            {/* Input Actions */}
            <div className="absolute right-2 top-2 flex items-center gap-1">
              <TouchButton
                variant="ghost"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                className="text-synrgy-muted hover:text-synrgy-primary"
              >
                <Paperclip className="w-4 h-4" />
              </TouchButton>

              <TouchButton
                variant="ghost"
                size="sm"
                onClick={isRecording ? stopRecording : startRecording}
                className={`${isRecording ? 'text-red-500' : 'text-synrgy-muted hover:text-synrgy-primary'}`}
              >
                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </TouchButton>
            </div>

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileAttachment}
              accept=".txt,.csv,.json,.log,.pcap"
            />
          </div>

          {/* Send Button */}
          <TouchButton
            variant="primary"
            onClick={handleSend}
            disabled={disabled || (!message.trim() && attachments.length === 0)}
            className={`
              ${isMobile ? 'min-w-[48px] h-12' : 'min-w-[44px] h-11'}
              flex-shrink-0 rounded-2xl
            `}
          >
            {disabled ? (
              <LoadingSpinner size="sm" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </TouchButton>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[
            "Show me recent alerts",
            "Analyze network traffic",
            "Security health check",
            "Top threats this week"
          ].map((suggestion, index) => (
            <TouchButton
              key={index}
              variant="ghost"
              size="sm"
              onClick={() => setMessage(suggestion)}
              className="text-xs text-synrgy-muted hover:text-synrgy-primary border border-synrgy-primary/20 rounded-full"
            >
              {suggestion}
            </TouchButton>
          ))}
        </div>
      </ResponsiveContainer>
    </div>
  )
}

// Main Chat Interface
export const EnhancedChatInterface: React.FC<ChatInterfaceProps> = ({
  messages = [],
  onSendMessage,
  onVoiceInput,
  isLoading = false,
  isTyping = false,
  placeholder,
  className = ''
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { showToast } = useToast()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSendMessage = (message: string, attachments?: File[]) => {
    onSendMessage?.(message, attachments)
  }

  const handleMessageAction = {
    regenerate: (messageId: string) => {
      showToast({
        type: 'info',
        title: 'Regenerating response...',
        message: 'Please wait while we generate a new response'
      })
    },
    copy: () => {},
    bookmark: () => {},
    feedback: (messageId: string, positive: boolean) => {
      showToast({
        type: 'success',
        title: 'Feedback received',
        message: `Thank you for your ${positive ? 'positive' : 'constructive'} feedback`
      })
    }
  }

  return (
    <div className={`flex flex-col h-full bg-synrgy-bg-950 ${className}`}>
      {/* Chat Header */}
      <div className="flex-shrink-0 border-b border-synrgy-primary/10 bg-synrgy-surface/50 backdrop-blur-sm">
        <ResponsiveContainer padding className="py-4">
          <div className="flex items-center gap-3">
            <motion.div
              className="w-12 h-12 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <Zap className="w-6 h-6 text-synrgy-bg-900" />
            </motion.div>
            
            <div>
              <h2 className="text-lg font-semibold text-synrgy-text">
                SYNRGY Assistant
              </h2>
              <p className="text-sm text-synrgy-muted">
                Your AI-powered security analyst
              </p>
            </div>

            <div className="flex-1" />

            <TouchButton
              variant="ghost"
              size="sm"
              className="text-synrgy-muted"
            >
              <MoreVertical className="w-5 h-5" />
            </TouchButton>
          </div>
        </ResponsiveContainer>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <ResponsiveContainer padding className="py-6 space-y-6">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <motion.div
                className="w-20 h-20 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center mx-auto mb-6"
                whileHover={{ scale: 1.1 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <Shield className="w-10 h-10 text-synrgy-bg-900" />
              </motion.div>
              
              <h3 className="text-2xl font-bold text-synrgy-text mb-2">
                Welcome to SYNRGY
              </h3>
              <p className="text-synrgy-muted mb-6 max-w-md mx-auto">
                Your AI-powered security analyst. Ask me about threats, analyze your data, 
                or get insights about your security posture.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {[
                  { icon: Shield, title: "Threat Analysis", desc: "Analyze threats and security events" },
                  { icon: Bot, title: "Smart Insights", desc: "Get AI-powered security insights" },
                  { icon: Zap, title: "Real-time Monitoring", desc: "Monitor your security posture" },
                  { icon: UserIcon, title: "Custom Queries", desc: "Ask anything about your data" }
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 + 0.3 }}
                    className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4 text-left"
                  >
                    <item.icon className="w-8 h-8 text-synrgy-primary mb-2" />
                    <h4 className="font-semibold text-synrgy-text mb-1">
                      {item.title}
                    </h4>
                    <p className="text-sm text-synrgy-muted">
                      {item.desc}
                    </p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Message List */}
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id || index}
              message={message}
              isUser={message.role === 'user'}
              onRegenerate={() => handleMessageAction.regenerate(message.id || '')}
              onCopy={handleMessageAction.copy}
              onBookmark={handleMessageAction.bookmark}
              onFeedback={(positive) => handleMessageAction.feedback(message.id || '', positive)}
            />
          ))}

          {/* Typing Indicator */}
          <AnimatePresence>
            {isTyping && <TypingIndicator />}
          </AnimatePresence>

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </ResponsiveContainer>
      </div>

      {/* Message Composer */}
      <MessageComposer
        onSend={handleSendMessage}
        onVoiceInput={onVoiceInput}
        placeholder={placeholder}
        disabled={isLoading}
      />
    </div>
  )
}

export default EnhancedChatInterface
