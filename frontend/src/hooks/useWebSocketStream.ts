/**
 * SYNRGY useWebSocketStream Hook
 * Real-time streaming chat responses with visual payloads
 * Based on SYNRGY.TXT streaming requirements
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  getWebSocketService,
  createWebSocketService,
  StreamingChatResponse,
} from '@/services/websocket'
import type { ChatMessage, VisualPayload } from '@/types'

export interface StreamingMessage {
  id: string
  conversationId: string
  role: 'user' | 'assistant'
  content: string
  visualPayload?: VisualPayload
  isStreaming: boolean
  isComplete: boolean
  metadata?: {
    confidence?: number
    dsl?: any
    kql?: string
    execution_time?: number
  }
  timestamp: string
  error?: string
}

export interface UseWebSocketStreamOptions {
  wsUrl?: string
  autoConnect?: boolean
  maxReconnectAttempts?: number
}

export interface UseWebSocketStreamReturn {
  // Connection state
  isConnected: boolean
  isConnecting: boolean

  // Streaming state
  isStreaming: boolean
  currentStream: StreamingMessage | null

  // Actions
  connect: () => Promise<void>
  disconnect: () => void
  sendMessage: (query: string, conversationId?: string, context?: any) => void

  // Error handling
  error: string | null
  clearError: () => void
}

export function useWebSocketStream(
  options: UseWebSocketStreamOptions = {}
): UseWebSocketStreamReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStream, setCurrentStream] = useState<StreamingMessage | null>(null)
  const [error, setError] = useState<string | null>(null)

  const wsServiceRef = useRef(getWebSocketService())
  const streamingTextRef = useRef<string>('')
  const currentMessageIdRef = useRef<string>('')

  // Reconnection state
  const reconnectAttemptRef = useRef(0)
  const maxReconnectAttempts = options.maxReconnectAttempts || 5
  const reconnectTimeoutRef = useRef<number | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const handleStreamingResponse = useCallback((response: StreamingChatResponse) => {
    console.log('📡 Streaming response:', response)

    // Use conversation_id as message identifier since message_id doesn't exist
    const messageId = response.conversation_id + '_' + Date.now()

    // Start or continue streaming for this message
    if (messageId !== currentMessageIdRef.current) {
      // New message started
      currentMessageIdRef.current = messageId
      streamingTextRef.current = ''
    }

    // Use accumulated_text or current_chunk
    if (response.current_chunk) {
      streamingTextRef.current += response.current_chunk
    } else if (response.accumulated_text) {
      streamingTextRef.current = response.accumulated_text
    }

    // Update the current streaming message
    const streamingMessage: StreamingMessage = {
      id: messageId,
      conversationId: response.conversation_id,
      role: 'assistant',
      content: streamingTextRef.current || response.accumulated_text,
      visualPayload: response.visual_payloads?.[0],
      isStreaming: !response.is_complete,
      isComplete: response.is_complete,
      metadata: response.metadata,
      timestamp: response.timestamp || new Date().toISOString(),
    }

    setCurrentStream(streamingMessage)
    setIsStreaming(!response.is_complete)
  }, [])

  const handleStreamingComplete = useCallback((response: StreamingChatResponse) => {
    console.log('✅ Stream complete:', response)

    const messageId = response.conversation_id + '_final'

    const finalMessage: StreamingMessage = {
      id: messageId,
      conversationId: response.conversation_id,
      role: 'assistant',
      content: response.accumulated_text || streamingTextRef.current,
      visualPayload: response.visual_payloads?.[0],
      isStreaming: false,
      isComplete: true,
      metadata: response.metadata,
      timestamp: response.timestamp || new Date().toISOString(),
    }

    setCurrentStream(finalMessage)
    setIsStreaming(false)

    // Clear refs for next message
    streamingTextRef.current = ''
    currentMessageIdRef.current = ''
  }, [])

  const handleStreamingError = useCallback((response: any) => {
    console.error('❌ Stream error:', response)

    setError('Failed to process your security query. Please try again.')
    setIsStreaming(false)
    setCurrentStream(null)

    // Clear refs
    streamingTextRef.current = ''
    currentMessageIdRef.current = ''
  }, [])

  const connect = useCallback(async () => {
    if (isConnecting || isConnected) return

    setIsConnecting(true)
    setError(null)

    try {
      // Create WebSocket service if not exists
      if (!wsServiceRef.current) {
        const wsUrl =
          options.wsUrl ||
          `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/ws/chat`.replace(
            'http',
            'ws'
          )
        wsServiceRef.current = createWebSocketService({
          url: wsUrl,
          autoReconnect: true,
          maxReconnectAttempts: options.maxReconnectAttempts || 5,
        })
      }

      // Setup callbacks
      wsServiceRef.current.setCallbacks({
        onConnect: () => {
          console.log('🔗 SYNRGY WebSocket connected')
          setIsConnected(true)
          setIsConnecting(false)
          setError(null)

          // Reset reconnection counter on successful connection
          reconnectAttemptRef.current = 0
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
            reconnectTimeoutRef.current = null
          }
        },
        onDisconnect: () => {
          console.log('🔌 SYNRGY WebSocket disconnected')
          setIsConnected(false)
          setIsStreaming(false)

          // Attempt automatic reconnection
          if (reconnectAttemptRef.current < maxReconnectAttempts) {
            const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttemptRef.current), 30000) // Max 30s
            console.log(
              `⏳ Attempting to reconnect in ${reconnectDelay}ms (attempt ${reconnectAttemptRef.current + 1}/${maxReconnectAttempts})`
            )

            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptRef.current += 1
              connect()
            }, reconnectDelay)
          } else {
            setError('Connection lost. Please refresh the page to reconnect.')
            reconnectAttemptRef.current = 0
          }
        },
        onError: error => {
          console.error('❌ WebSocket error:', error)
          setError('Connection failed. Please check your network.')
          setIsConnecting(false)
          setIsConnected(false)
        },
        onChatStream: handleStreamingResponse,
        onChatComplete: handleStreamingComplete,
        onChatError: handleStreamingError,
      })

      // Connect
      await wsServiceRef.current.connect()
    } catch (err) {
      console.error('Failed to connect:', err)
      setError(err instanceof Error ? err.message : 'Connection failed')
      setIsConnecting(false)
    }
  }, [
    isConnecting,
    isConnected,
    options.wsUrl,
    options.maxReconnectAttempts,
    handleStreamingResponse,
    handleStreamingComplete,
    handleStreamingError,
  ])

  const disconnect = useCallback(() => {
    // Clear any pending reconnection attempts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    reconnectAttemptRef.current = 0

    wsServiceRef.current?.disconnect()
    setIsConnected(false)
    setIsStreaming(false)
    setCurrentStream(null)
  }, [])

  const sendMessage = useCallback(
    (query: string, conversationId?: string, context?: any) => {
      if (!wsServiceRef.current || !isConnected) {
        setError('Not connected to server')
        return
      }

      console.log('📤 Sending message:', query)
      setError(null)

      // Send the message via WebSocket
      const success = wsServiceRef.current.sendChatMessage(query, conversationId, context)

      if (!success) {
        setError('Failed to send message. Please check your connection.')
      }
    },
    [isConnected]
  )

  // Auto-connect on mount
  useEffect(() => {
    if (options.autoConnect !== false) {
      connect()
    }

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      disconnect()
    }
  }, []) // Only run once on mount

  return {
    isConnected,
    isConnecting,
    isStreaming,
    currentStream,
    connect,
    disconnect,
    sendMessage,
    error,
    clearError,
  }
}
