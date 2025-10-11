import { useState, type CSSProperties } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Bot, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Copy,
  Code,
  Download
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import ReactMarkdown, { type Components } from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

import type { ChatMessage } from '@/types'
import VisualRenderer from './VisualRenderer'
import { useChatStore } from '@/stores/chatStore'
import PinToDashboardButton from './PinToDashboardButton'

interface MessageBubbleProps {
  message: ChatMessage
  isLatest?: boolean
}

const syntaxStyle = oneDark as { [key: string]: CSSProperties }

const markdownComponents: Components = {
  code({ inline, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className ?? '')
    if (!inline && match) {
      return (
        <SyntaxHighlighter
          style={syntaxStyle}
          language={match[1]}
          PreTag="div"
          className="rounded-lg !bg-synrgy-bg-900 !text-sm"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      )
    }

    return (
      <code className={`${className ?? ''} bg-synrgy-bg-900/50 px-1 rounded`} {...props}>
        {children}
      </code>
    )
  }
}

export default function MessageBubble({ message, isLatest: _isLatest = false }: MessageBubbleProps) {
  const [showExplain, setShowExplain] = useState(false)
  const [copied, setCopied] = useState(false)
  const { showExplainQuery, selectMessage, selectedMessageId } = useChatStore()
  
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const isSelected = selectedMessageId === message.id
  
  // isLatest parameter is available for future message highlighting features

  const getStatusIcon = () => {
    switch (message.status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-synrgy-muted animate-spin" />
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'clarification_needed':
        return <AlertCircle className="w-4 h-4 text-synrgy-accent" />
      default:
        return null
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    } catch {
      return 'just now'
    }
  }

  // System messages (like errors or notifications)
  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="flex justify-center my-4"
      >
        <div className="chat-bubble-system max-w-md">
          <AlertCircle className="w-4 h-4 inline-block mr-2" />
          {message.content}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={`flex gap-3 mb-6 group ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-synrgy-primary text-synrgy-bg-900' 
          : 'bg-gradient-to-br from-synrgy-primary/20 to-synrgy-accent/20 border border-synrgy-primary/30'
      }`}>
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <Bot className="w-5 h-5 text-synrgy-primary" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Message Bubble */}
        <div
          className={`relative ${isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'} ${
            isSelected ? 'ring-2 ring-synrgy-primary/50' : ''
          } ${message.status === 'pending' ? 'opacity-75' : ''}`}
          onClick={() => selectMessage(isSelected ? null : message.id)}
        >
          {/* Loading indicator for pending messages */}
          {message.status === 'pending' && (
            <div className="flex items-center gap-2 mb-2">
              <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-synrgy-primary rounded-full"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.5, 1, 0.5]
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: i * 0.2
                    }}
                  />
                ))}
              </div>
              <span className="text-xs text-synrgy-muted">SYNRGY is thinking...</span>
            </div>
          )}

          {/* Message Text */}
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown components={markdownComponents}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Error Message */}
          {message.error && (
            <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <XCircle className="w-4 h-4" />
                <span>Error: {message.error}</span>
              </div>
            </div>
          )}

          {/* Visual Payload */}
          {message.visual_payload && (
            <div className="mt-4 space-y-3">
              <VisualRenderer payload={message.visual_payload} />
              
              {/* Pin to Dashboard Button */}
              <div className="flex justify-end">
                <PinToDashboardButton 
                  message={message}
                  visualPayload={message.visual_payload}
                />
              </div>
            </div>
          )}

          {/* Message Actions */}
          <div className={`flex items-center gap-2 mt-3 ${isUser ? 'justify-start' : 'justify-end'}`}>
            {/* Copy button */}
            <button
              onClick={(e) => {
                e.stopPropagation()
                copyToClipboard(message.content)
              }}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-synrgy-primary/10 rounded text-synrgy-muted hover:text-synrgy-primary"
              title="Copy message"
            >
              {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>

            {/* Show query button for assistant messages */}
            {!isUser && message.metadata?.intent && showExplainQuery && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setShowExplain(!showExplain)
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-synrgy-accent/10 rounded text-synrgy-muted hover:text-synrgy-accent"
                title="Show generated query"
              >
                <Code className="w-4 h-4" />
              </button>
            )}

            {/* Export data button */}
            {message.visual_payload && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  // TODO: Implement data export
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-synrgy-primary/10 rounded text-synrgy-muted hover:text-synrgy-primary"
                title="Export data"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Query Explanation */}
        {showExplain && message.metadata && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 w-full bg-synrgy-surface/50 border border-synrgy-primary/20 rounded-lg p-4"
          >
            <div className="text-xs text-synrgy-muted mb-2">Generated Query Details</div>
            
            {/* Intent and Confidence */}
            <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
              <div>
                <span className="text-synrgy-muted">Intent:</span>
                <span className="ml-2 text-synrgy-primary">{message.metadata.intent}</span>
              </div>
              <div>
                <span className="text-synrgy-muted">Confidence:</span>
                <span className="ml-2 text-synrgy-accent">
                  {((message.metadata.confidence || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Processing Time */}
            {message.metadata.processing_time && (
              <div className="text-xs text-synrgy-muted">
                Processed in {message.metadata.processing_time.toFixed(2)}ms
              </div>
            )}

            {/* Results Count */}
            {message.metadata.total_results && (
              <div className="text-xs text-synrgy-muted">
                {message.metadata.total_results} results found
              </div>
            )}
          </motion.div>
        )}

        {/* Timestamp and Status */}
        <div className={`flex items-center gap-2 mt-2 text-xs text-synrgy-muted ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}>
          <span>{formatTimestamp(message.timestamp)}</span>
          {getStatusIcon()}
        </div>
      </div>
    </motion.div>
  )
}
