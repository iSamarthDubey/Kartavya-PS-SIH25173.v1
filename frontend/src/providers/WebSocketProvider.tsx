/**
 * SYNRGY WebSocket Provider
 * Handles real-time chat communication with backend WebSocket endpoints
 * NO STATIC DATA - All messages come from backend streaming
 */

import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { useAuth } from './AuthProvider'
import { toast } from 'react-hot-toast'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

interface ChatMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  status: 'processing' | 'success' | 'error' | 'clarification_needed'
  stage?: string
  metadata?: any
  visual_payload?: any
  timestamp: string
}

interface WebSocketContextType {
  isConnected: boolean
  messages: ChatMessage[]
  sendMessage: (message: string, conversationId?: string) => void
  clearMessages: () => void
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: React.ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { isAuthenticated, token } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  // Get WebSocket URL from environment
  const getWebSocketUrl = () => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const wsUrl = baseUrl.replace('http', 'ws')
    return `${wsUrl}/ws/chat` // Using simple endpoint without session_id requirement
  }

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setConnectionStatus('connecting')
    
    try {
      const wsUrl = getWebSocketUrl()
      console.log('Connecting to WebSocket:', wsUrl)
      
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionStatus('connected')
        reconnectAttempts.current = 0
        
        // Send authentication if we have a token
        if (token) {
          wsRef.current?.send(JSON.stringify({
            type: 'auth',
            data: { token }
          }))
        }
      }

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleIncomingMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setConnectionStatus('disconnected')
        
        // Attempt to reconnect if not intentionally closed
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          console.log(`Reconnecting in ${timeout}ms...`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, timeout)
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionStatus('error')
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected')
      wsRef.current = null
    }
    
    setIsConnected(false)
    setConnectionStatus('disconnected')
  }

  const handleIncomingMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket connection confirmed')
        break
        
      case 'chat_response':
        // Real-time chat response from backend
        const chatMessage: ChatMessage = {
          id: message.data.id,
          conversation_id: message.data.conversation_id,
          role: message.data.role,
          content: message.data.content,
          status: message.data.status,
          stage: message.data.stage,
          metadata: message.data.metadata,
          visual_payload: message.data.visual_payload,
          timestamp: message.timestamp
        }
        
        setMessages(prev => {
          // Update existing message or add new one
          const existingIndex = prev.findIndex(msg => msg.id === chatMessage.id)
          if (existingIndex >= 0) {
            const updated = [...prev]
            updated[existingIndex] = chatMessage
            return updated
          } else {
            return [...prev, chatMessage]
          }
        })
        break
        
      case 'processing_started':
        // Backend started processing query
        const processingMessage: ChatMessage = {
          id: message.data.message_id,
          conversation_id: message.data.conversation_id,
          role: 'assistant',
          content: 'Processing your query...',
          status: 'processing',
          timestamp: message.timestamp
        }
        setMessages(prev => [...prev, processingMessage])
        break
        
      case 'error':
        toast.error(message.data.message || 'WebSocket error')
        break
        
      case 'pong':
        // Keep-alive response
        break
        
      default:
        console.log('Unknown WebSocket message type:', message.type)
    }
  }

  const sendMessage = (messageText: string, conversationId?: string) => {
    if (!isConnected || !wsRef.current) {
      toast.error('Not connected to chat service')
      return
    }

    // Add user message immediately (optimistic update)
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      conversation_id: conversationId || `conv_${Date.now()}`,
      role: 'user',
      content: messageText,
      status: 'success',
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])

    // Send to backend
    wsRef.current.send(JSON.stringify({
      type: 'chat_message',
      data: {
        query: messageText,
        conversation_id: conversationId || userMessage.conversation_id,
        context: {} // Additional context can be added here
      }
    }))
  }

  const clearMessages = () => {
    setMessages([])
  }

  // Connect when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticated])

  // Send periodic ping to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          data: {},
          timestamp: new Date().toISOString()
        }))
      }
    }, 30000) // Ping every 30 seconds

    return () => clearInterval(pingInterval)
  }, [isConnected])

  const contextValue: WebSocketContextType = {
    isConnected,
    messages,
    sendMessage,
    clearMessages,
    connectionStatus,
  }

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  )
}
