import { useEffect, useRef, useCallback, useState } from 'react'
import { ChatMessage, WebSocketMessage } from '../types'
import { createWebSocketService, getWebSocketService, WebSocketService, WebSocketCallbacks } from '../services/websocket'
import { useAppStore } from '../stores/appStore'

interface UseWebSocketOptions {
  url?: string
  autoConnect?: boolean
  onChatMessage?: (message: ChatMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

interface UseWebSocketReturn {
  isConnected: boolean
  isReconnecting: boolean
  reconnectAttempts: number
  sendMessage: (message: WebSocketMessage) => boolean
  sendChatMessage: (query: string, conversationId?: string, context?: any) => boolean
  connect: () => Promise<void>
  disconnect: () => void
  connectionState: 'connecting' | 'open' | 'closing' | 'closed'
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [isReconnecting, setIsReconnecting] = useState(false)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [connectionState, setConnectionState] = useState<'connecting' | 'open' | 'closing' | 'closed'>('closed')
  
  const wsServiceRef = useRef<WebSocketService | null>(null)
  const { user, token } = useAppStore()

  // Get WebSocket URL from environment or default
  const wsUrl = options.url || `ws://localhost:8001/ws`

  const updateConnectionState = useCallback(() => {
    const service = wsServiceRef.current
    if (!service) {
      setConnectionState('closed')
      setIsConnected(false)
      return
    }

    const readyState = service.getReadyState()
    switch (readyState) {
      case WebSocket.CONNECTING:
        setConnectionState('connecting')
        setIsConnected(false)
        break
      case WebSocket.OPEN:
        setConnectionState('open')
        setIsConnected(true)
        break
      case WebSocket.CLOSING:
        setConnectionState('closing')
        setIsConnected(false)
        break
      case WebSocket.CLOSED:
        setConnectionState('closed')
        setIsConnected(false)
        break
    }
  }, [])

  const connect = useCallback(async () => {
    try {
      // Create or get existing service
      if (!wsServiceRef.current) {
        wsServiceRef.current = createWebSocketService({
          url: wsUrl,
          token: token || undefined,
          autoReconnect: true,
          maxReconnectAttempts: 5,
          reconnectDelay: 3000
        })
      }

      const callbacks: WebSocketCallbacks = {
        onConnect: () => {
          console.log('WebSocket connected successfully')
          setIsConnected(true)
          setIsReconnecting(false)
          setReconnectAttempts(0)
          updateConnectionState()
          options.onConnect?.()
        },

        onDisconnect: () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          updateConnectionState()
          options.onDisconnect?.()
        },

        onError: (error) => {
          console.error('WebSocket error:', error)
          updateConnectionState()
          options.onError?.(error)
        },

        onReconnecting: (attempt) => {
          console.log(`WebSocket reconnecting (attempt ${attempt})`)
          setIsReconnecting(true)
          setReconnectAttempts(attempt)
        },

        onChatMessage: (message) => {
          console.log('Chat message received:', message)
          options.onChatMessage?.(message)
        }
      }

      await wsServiceRef.current.connect(callbacks)
      updateConnectionState()

    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      updateConnectionState()
      throw error
    }
  }, [wsUrl, token, options, updateConnectionState])

  const disconnect = useCallback(() => {
    if (wsServiceRef.current) {
      wsServiceRef.current.disconnect()
      setIsConnected(false)
      setIsReconnecting(false)
      setReconnectAttempts(0)
      updateConnectionState()
    }
  }, [updateConnectionState])

  const sendMessage = useCallback((message: WebSocketMessage): boolean => {
    if (!wsServiceRef.current) {
      console.warn('WebSocket service not initialized')
      return false
    }
    return wsServiceRef.current.send(message)
  }, [])

  const sendChatMessage = useCallback((query: string, conversationId?: string, context?: any): boolean => {
    if (!wsServiceRef.current) {
      console.warn('WebSocket service not initialized')
      return false
    }
    return wsServiceRef.current.sendChatMessage(query, conversationId, context)
  }, [])

  // Auto-connect when user is authenticated and autoConnect is true
  useEffect(() => {
    if (options.autoConnect !== false && user && token && !isConnected && !isReconnecting) {
      connect().catch(error => {
        console.error('Auto-connect failed:', error)
      })
    }
  }, [user, token, isConnected, isReconnecting, connect, options.autoConnect])

  // Update token when it changes
  useEffect(() => {
    if (wsServiceRef.current && token) {
      wsServiceRef.current.updateConfig({ token })
    }
  }, [token])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsServiceRef.current) {
        wsServiceRef.current.disconnect()
      }
    }
  }, [])

  return {
    isConnected,
    isReconnecting,
    reconnectAttempts,
    sendMessage,
    sendChatMessage,
    connect,
    disconnect,
    connectionState
  }
}

// Hook for streaming chat messages
export function useStreamingChat() {
  const [streamingMessage, setStreamingMessage] = useState<string>('')
  const [isStreaming, setIsStreaming] = useState(false)
  const streamingMessageRef = useRef<string>('')

  const wsService = getWebSocketService()

  const handleStreamingMessage = useCallback((message: ChatMessage) => {
    if (message.status === 'pending') {
      // This is a streaming chunk
      setIsStreaming(true)
      streamingMessageRef.current += message.content
      setStreamingMessage(streamingMessageRef.current)
    } else {
      // Final message
      setIsStreaming(false)
      streamingMessageRef.current = ''
      setStreamingMessage('')
    }
  }, [])

  const startNewStream = useCallback(() => {
    streamingMessageRef.current = ''
    setStreamingMessage('')
    setIsStreaming(false)
  }, [])

  const sendStreamingQuery = useCallback((query: string, conversationId?: string, context?: any) => {
    if (!wsService) {
      console.warn('WebSocket service not available')
      return false
    }

    startNewStream()
    return wsService.sendChatMessage(query, conversationId, context)
  }, [wsService, startNewStream])

  return {
    streamingMessage,
    isStreaming,
    sendStreamingQuery,
    startNewStream,
    handleStreamingMessage
  }
}
