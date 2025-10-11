import { WebSocketMessage, ChatMessage } from '../types'
import { useAppStore } from '../stores/appStore'

export interface WebSocketConfig {
  url: string
  token?: string
  autoReconnect?: boolean
  maxReconnectAttempts?: number
  reconnectDelay?: number
}

export interface WebSocketCallbacks {
  onMessage?: (message: WebSocketMessage) => void
  onChatMessage?: (message: ChatMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  onReconnecting?: (attempt: number) => void
}

class WebSocketService {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private callbacks: WebSocketCallbacks = {}
  private reconnectAttempts = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  private heartbeatTimer: NodeJS.Timeout | null = null
  private isReconnecting = false
  private isManuallyDisconnected = false

  constructor(config: WebSocketConfig) {
    this.config = {
      autoReconnect: true,
      maxReconnectAttempts: 5,
      reconnectDelay: 3000,
      ...config
    }
  }

  connect(callbacks?: WebSocketCallbacks): Promise<void> {
    if (callbacks) {
      this.callbacks = { ...this.callbacks, ...callbacks }
    }

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = new URL(this.config.url)
        if (this.config.token) {
          wsUrl.searchParams.set('token', this.config.token)
        }

        this.ws = new WebSocket(wsUrl.toString())
        this.isManuallyDisconnected = false

        this.ws.onopen = (event) => {
          console.log('WebSocket connected:', wsUrl.toString())
          this.reconnectAttempts = 0
          this.isReconnecting = false
          this.startHeartbeat()
          this.callbacks.onConnect?.()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error, event.data)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.stopHeartbeat()
          this.callbacks.onDisconnect?.()

          if (!this.isManuallyDisconnected && this.config.autoReconnect) {
            this.attemptReconnect()
          }
        }

        this.ws.onerror = (event) => {
          console.error('WebSocket error:', event)
          this.callbacks.onError?.(event)
          reject(new Error('WebSocket connection failed'))
        }

      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(message: WebSocketMessage) {
    // Call general message callback
    this.callbacks.onMessage?.(message)

    // Handle specific message types
    switch (message.type) {
      case 'chat_response':
        if (message.data && this.callbacks.onChatMessage) {
          // Convert WebSocket message data to ChatMessage format
          const chatMessage: ChatMessage = {
            id: message.data.id || `ws_${Date.now()}`,
            conversation_id: message.data.conversation_id || '',
            role: message.data.role || 'assistant',
            content: message.data.content || '',
            timestamp: message.timestamp,
            metadata: message.data.metadata,
            visual_payload: message.data.visual_payload,
            status: message.data.status || 'success'
          }
          this.callbacks.onChatMessage(chatMessage)
        }
        break

      case 'notification':
        // Handle system notifications
        if (message.data) {
          const { addNotification } = useAppStore.getState()
          addNotification({
            id: `ws_${Date.now()}`,
            type: message.data.type || 'info',
            title: message.data.title || 'Notification',
            message: message.data.message || '',
            timestamp: message.timestamp
          })
        }
        break

      case 'system_update':
        // Handle system-wide updates
        console.log('System update received:', message.data)
        break

      case 'error':
        console.error('WebSocket error message:', message.data)
        break

      default:
        console.log('Unknown WebSocket message type:', message.type)
    }
  }

  private attemptReconnect() {
    if (this.isReconnecting || 
        this.reconnectAttempts >= (this.config.maxReconnectAttempts || 5)) {
      console.log('Max reconnection attempts reached')
      return
    }

    this.isReconnecting = true
    this.reconnectAttempts++

    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`)
    this.callbacks.onReconnecting?.(this.reconnectAttempts)

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
        this.attemptReconnect()
      })
    }, this.config.reconnectDelay || 3000)
  }

  private startHeartbeat() {
    // Send heartbeat every 30 seconds
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          data: {},
          timestamp: new Date().toISOString()
        })
      }
    }, 30000)
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  send(message: WebSocketMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
        return false
      }
    }
    return false
  }

  // Send a chat message with streaming support
  sendChatMessage(query: string, conversationId?: string, context?: any): boolean {
    return this.send({
      type: 'chat_message',
      data: {
        query,
        conversation_id: conversationId,
        context,
        stream: true // Enable streaming response
      },
      session_id: conversationId,
      timestamp: new Date().toISOString()
    })
  }

  disconnect() {
    this.isManuallyDisconnected = true
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect')
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  updateConfig(newConfig: Partial<WebSocketConfig>) {
    this.config = { ...this.config, ...newConfig }
  }

  setCallbacks(callbacks: WebSocketCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks }
  }
}

// Global WebSocket service instance
let wsService: WebSocketService | null = null

export function createWebSocketService(config: WebSocketConfig): WebSocketService {
  if (wsService) {
    wsService.disconnect()
  }
  
  wsService = new WebSocketService(config)
  return wsService
}

export function getWebSocketService(): WebSocketService | null {
  return wsService
}

export { WebSocketService }
