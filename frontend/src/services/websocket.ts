import { WebSocketMessage, ChatMessage, VisualPayload, StreamingChatResponse } from '../types'

// Re-export for external use
export type { StreamingChatResponse }
import { useAppStore } from '../stores/appStore'

// Backend WebSocket message format adapter - ACTUAL BACKEND FORMAT
interface BackendStreamingResponse {
  id: string
  conversation_id: string
  role: string
  content: string
  status: 'processing' | 'success' | 'error' | 'clarification_needed'
  stage: 'nlp_processing' | 'query_building' | 'siem_query' | 'complete' | 'error'
  visual_payload?: VisualPayload
  metadata?: {
    intent?: string
    confidence?: number
    entities?: any[]
    results_count?: number
    processing_time?: number
    execution_time?: number
  }
}

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
  onChatStream?: (response: StreamingChatResponse) => void
  onChatComplete?: (response: StreamingChatResponse) => void
  onChatError?: (response: BackendStreamingResponse) => void
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
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private isReconnecting = false
  private isManuallyDisconnected = false

  constructor(config: WebSocketConfig) {
    this.config = {
      autoReconnect: true,
      maxReconnectAttempts: 5,
      reconnectDelay: 3000,
      ...config,
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

        this.ws.onopen = event => {
          this.reconnectAttempts = 0
          this.isReconnecting = false
          this.startHeartbeat()
          this.callbacks.onConnect?.()
          resolve()
        }

        this.ws.onmessage = event => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = event => {
          this.stopHeartbeat()
          this.callbacks.onDisconnect?.()

          if (!this.isManuallyDisconnected && this.config.autoReconnect) {
            this.attemptReconnect()
          }
        }

        this.ws.onerror = event => {
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
        if (message.data) {
          // Convert backend format to frontend format
          const backendResponse = message.data as BackendStreamingResponse

          const frontendResponse: StreamingChatResponse = {
            conversation_id: backendResponse.conversation_id,
            role: 'assistant',
            accumulated_text: backendResponse.content || '',
            current_chunk: backendResponse.content,
            is_complete:
              backendResponse.status === 'success' || backendResponse.stage === 'complete',
            timestamp: message.timestamp,
            visual_payloads: backendResponse.visual_payload
              ? [backendResponse.visual_payload]
              : undefined,
            metadata: {
              processing_step: backendResponse.stage
                ? backendResponse.stage.replace('_', ' ').toUpperCase()
                : 'Processing...',
              confidence: backendResponse.metadata?.confidence,
              execution_time:
                backendResponse.metadata?.execution_time ||
                backendResponse.metadata?.processing_time,
              intent: backendResponse.metadata?.intent,
              entities: backendResponse.metadata?.entities,
            },
            error: backendResponse.status === 'error' ? backendResponse.content : undefined,
          }

          // Call streaming callback with converted data
          this.callbacks.onChatStream?.(frontendResponse)

          // Handle completion
          if (backendResponse.status === 'success' || backendResponse.stage === 'complete') {
            this.callbacks.onChatComplete?.(frontendResponse)

            // Also create a complete ChatMessage for compatibility
            if (this.callbacks.onChatMessage) {
              const chatMessage: ChatMessage = {
                id: backendResponse.id,
                conversation_id: backendResponse.conversation_id,
                role:
                  backendResponse.role === 'user' || backendResponse.role === 'system'
                    ? (backendResponse.role as 'user' | 'system')
                    : 'assistant',
                content: backendResponse.content || '',
                timestamp: message.timestamp,
                metadata: backendResponse.metadata,
                visual_payload: backendResponse.visual_payload,
                status: backendResponse.status === 'error' ? 'error' : 'success',
              }
              this.callbacks.onChatMessage(chatMessage)
            }
          }

          // Handle errors
          if (backendResponse.status === 'error') {
            this.callbacks.onChatError?.(backendResponse)
          }
        }
        break

      case 'notification':
        // Handle system notifications
        if (message.data) {
          const { addNotification } = useAppStore.getState()
          addNotification({
            type: message.data.type || 'info',
            title: message.data.title || 'Notification',
            message: message.data.message || '',
            timestamp: message.timestamp,
            read: false
          })
        }
        break

      case 'system_update':
        // Handle system-wide updates (silent)
        break

      case 'error':
        console.error('WebSocket error message:', message.data)
        break

      default:
      // Unknown message type - ignore silently in production
    }
  }

  private attemptReconnect() {
    if (this.isReconnecting || this.reconnectAttempts >= (this.config.maxReconnectAttempts || 5)) {
      console.log('Max reconnection attempts reached')
      return
    }

    this.isReconnecting = true
    this.reconnectAttempts++

    if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
      console.log(
        `Attempting to reconnect... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`
      )
    }
    this.callbacks.onReconnecting?.(this.reconnectAttempts)

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
          console.error('Reconnection failed:', error)
        }
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
          timestamp: new Date().toISOString(),
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
        if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
          console.error('Failed to send WebSocket message:', error)
        }
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
        stream: true, // Enable streaming response
      },
      session_id: conversationId,
      timestamp: new Date().toISOString(),
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
