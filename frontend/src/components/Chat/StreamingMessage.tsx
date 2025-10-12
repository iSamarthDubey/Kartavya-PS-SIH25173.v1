import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, Eye, Bot, User } from 'lucide-react'
import { useState, useEffect } from 'react'

import type { ChatMessage, StreamingChatResponse } from '@/types'
import VisualRenderer from '@/components/Visuals/VisualRenderer'

interface StreamingMessageProps {
  message?: ChatMessage
  stream?: StreamingChatResponse
  isStreaming?: boolean
  className?: string
}

export default function StreamingMessage({ 
  message, 
  stream, 
  isStreaming = false,
  className = '' 
}: StreamingMessageProps) {
  const [displayText, setDisplayText] = useState('')
  const [visiblePayloads, setVisiblePayloads] = useState<any[]>([])

  // Handle streaming text accumulation
  useEffect(() => {
    if (stream) {
      setDisplayText(stream.accumulated_text || '')
      
      // Add visual payloads as they arrive
      if (stream.visual_payloads && stream.visual_payloads.length > 0) {
        setVisiblePayloads(stream.visual_payloads)
      }
    } else if (message) {
      setDisplayText(message.content)
    }
  }, [stream, message])

  // Use streaming data or fallback to message
  const isAssistant = message?.role === 'assistant' || stream?.role === 'assistant'
  const messageId = message?.id || stream?.conversation_id || 'streaming'
  const timestamp = message?.timestamp || stream?.timestamp || new Date().toISOString()

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-4 group ${className}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isAssistant 
          ? 'bg-gradient-to-br from-synrgy-primary/20 to-synrgy-accent/20 border border-synrgy-primary/30'
          : 'bg-synrgy-surface border border-synrgy-primary/20'
      }`}>
        {isAssistant ? (
          <Bot className="w-4 h-4 text-synrgy-primary" />
        ) : (
          <User className="w-4 h-4 text-synrgy-muted" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* Message Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-synrgy-text">
            {isAssistant ? 'SYNRGY Assistant' : 'You'}
          </span>
          
          <span className="text-xs text-synrgy-muted">
            {new Date(timestamp).toLocaleTimeString()}
          </span>

          {isStreaming && (
            <div className="flex items-center gap-1 text-synrgy-accent">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span className="text-xs">Streaming...</span>
            </div>
          )}

          {/* Message status */}
          {message?.status === 'error' && (
            <div className="flex items-center gap-1 text-red-400">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span className="text-xs">Error</span>
            </div>
          )}
        </div>

        {/* Text Content */}
        <div className="prose prose-sm max-w-none text-synrgy-text">
          {displayText ? (
            <div className="whitespace-pre-wrap">
              {displayText}
              {isStreaming && (
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="inline-block w-2 h-4 bg-synrgy-primary ml-1"
                />
              )}
            </div>
          ) : isStreaming ? (
            <div className="flex items-center gap-2 text-synrgy-muted">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating response...</span>
            </div>
          ) : null}
        </div>

        {/* Visual Payloads */}
        <AnimatePresence>
          {visiblePayloads.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 space-y-4"
            >
              {visiblePayloads.map((payload, index) => (
                <motion.div
                  key={`payload-${index}`}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-synrgy-primary/20 rounded-lg overflow-hidden bg-synrgy-surface/30"
                >
                  <VisualRenderer
                    payload={payload}
                    messageId={messageId}
                    conversationId={stream?.conversation_id || message?.conversation_id}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Details */}
        {message?.error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
          >
            <div className="text-sm text-red-400">
              <strong>Error:</strong> {message.error}
            </div>
          </motion.div>
        )}

        {/* Streaming Error */}
        {stream?.error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
          >
            <div className="text-sm text-red-400">
              <strong>Streaming Error:</strong> {stream.error}
            </div>
          </motion.div>
        )}

        {/* Metadata (Debug) */}
        {message?.metadata && (
          <details className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
            <summary className="text-xs text-synrgy-muted cursor-pointer flex items-center gap-1">
              <Eye className="w-3 h-3" />
              View metadata
            </summary>
            <div className="mt-2 p-2 bg-synrgy-surface/50 rounded text-xs text-synrgy-muted font-mono">
              <pre>{JSON.stringify(message.metadata, null, 2)}</pre>
            </div>
          </details>
        )}
      </div>
    </motion.div>
  )
}
