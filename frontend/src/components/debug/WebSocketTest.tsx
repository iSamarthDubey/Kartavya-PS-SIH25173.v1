import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wifi, WifiOff, Play, Square, Send } from 'lucide-react'
import { useWebSocket, useStreamingChat } from '../../hooks/useWebSocket'
import { ChatMessage } from '../../types'

interface WebSocketTestProps {
  className?: string
}

export default function WebSocketTest({ className = '' }: WebSocketTestProps) {
  const [testMessage, setTestMessage] = useState('Show me failed login attempts in the last hour')
  const [receivedMessages, setReceivedMessages] = useState<ChatMessage[]>([])
  const [connectionLogs, setConnectionLogs] = useState<string[]>([])

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setConnectionLogs(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 19)])
  }

  const { 
    isConnected, 
    isReconnecting, 
    reconnectAttempts, 
    connectionState,
    sendMessage,
    sendChatMessage,
    connect,
    disconnect 
  } = useWebSocket({
    autoConnect: false, // Manual connection for testing
    onChatMessage: (message: ChatMessage) => {
      addLog(`Received chat message: ${message.content.substring(0, 50)}...`)
      setReceivedMessages(prev => [message, ...prev.slice(0, 9)])
    },
    onConnect: () => {
      addLog('WebSocket connected successfully')
    },
    onDisconnect: () => {
      addLog('WebSocket disconnected')
    },
    onError: (error) => {
      addLog(`WebSocket error: ${error.type}`)
    }
  })

  const { streamingMessage, isStreaming, sendStreamingQuery } = useStreamingChat()

  const handleConnect = async () => {
    try {
      addLog('Attempting to connect...')
      await connect()
    } catch (error: any) {
      addLog(`Connection failed: ${error.message}`)
    }
  }

  const handleDisconnect = () => {
    addLog('Disconnecting...')
    disconnect()
  }

  const handleSendTest = () => {
    if (!testMessage.trim()) return

    addLog(`Sending test message: ${testMessage}`)
    
    if (isConnected) {
      const success = sendStreamingQuery(testMessage, 'test_conversation')
      if (!success) {
        addLog('Failed to send streaming message')
      }
    } else {
      addLog('Not connected - cannot send message')
    }
  }

  const handleSendRaw = () => {
    if (!isConnected) {
      addLog('Not connected - cannot send raw message')
      return
    }

    const rawMessage = {
      type: 'ping' as const,
      data: { test: true, timestamp: Date.now() },
      timestamp: new Date().toISOString()
    }

    addLog(`Sending raw message: ${JSON.stringify(rawMessage)}`)
    const success = sendMessage(rawMessage)
    
    if (!success) {
      addLog('Failed to send raw message')
    }
  }

  // Connection status indicator
  const getStatusColor = () => {
    if (isConnected) return 'text-green-500'
    if (isReconnecting) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getStatusIcon = () => {
    if (isConnected) return <Wifi className="w-4 h-4" />
    if (isReconnecting) return <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
    return <WifiOff className="w-4 h-4" />
  }

  const getStatusText = () => {
    if (isConnected) return 'Connected'
    if (isReconnecting) return `Reconnecting... (${reconnectAttempts})`
    return 'Disconnected'
  }

  return (
    <div className={`bg-synrgy-surface border border-synrgy-primary/20 rounded-xl p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-synrgy-text">WebSocket Test</h2>
          <div className={`flex items-center gap-2 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="text-sm">{getStatusText()}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {!isConnected ? (
            <button
              onClick={handleConnect}
              disabled={isReconnecting}
              className="px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 disabled:opacity-50 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Connect
            </button>
          ) : (
            <button
              onClick={handleDisconnect}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center gap-2"
            >
              <Square className="w-4 h-4" />
              Disconnect
            </button>
          )}
        </div>
      </div>

      {/* Connection Details */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-synrgy-bg-900/50 rounded-lg p-4">
          <div className="text-sm text-synrgy-muted mb-2">Connection State</div>
          <div className="text-synrgy-text font-medium">{connectionState}</div>
        </div>
        
        <div className="bg-synrgy-bg-900/50 rounded-lg p-4">
          <div className="text-sm text-synrgy-muted mb-2">Streaming</div>
          <div className={`font-medium ${isStreaming ? 'text-synrgy-accent' : 'text-synrgy-text'}`}>
            {isStreaming ? 'Active' : 'Inactive'}
          </div>
        </div>
      </div>

      {/* Test Controls */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm text-synrgy-muted mb-2">Test Message</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Enter test message..."
              className="flex-1 bg-synrgy-bg-900/50 border border-synrgy-primary/20 rounded-lg px-3 py-2 text-synrgy-text placeholder:text-synrgy-muted focus:border-synrgy-primary/50 outline-none"
            />
            <button
              onClick={handleSendTest}
              disabled={!isConnected || !testMessage.trim() || isStreaming}
              className="px-4 py-2 bg-synrgy-accent text-synrgy-bg-900 rounded-lg hover:bg-synrgy-accent/90 disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send Chat
            </button>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleSendRaw}
            disabled={!isConnected}
            className="px-4 py-2 bg-synrgy-primary/10 text-synrgy-primary border border-synrgy-primary/20 rounded-lg hover:bg-synrgy-primary/20 disabled:opacity-50"
          >
            Send Ping
          </button>
        </div>
      </div>

      {/* Streaming Message Display */}
      {streamingMessage && (
        <div className="mb-6">
          <div className="text-sm text-synrgy-muted mb-2">Live Stream:</div>
          <div className="bg-synrgy-accent/10 border border-synrgy-accent/20 rounded-lg p-3">
            <div className="text-synrgy-text text-sm">
              {streamingMessage}
              {isStreaming && (
                <span className="inline-block w-2 h-5 bg-synrgy-accent ml-1 animate-pulse" />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Connection Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="text-sm text-synrgy-muted mb-2">Connection Logs</div>
          <div className="bg-synrgy-bg-900/50 rounded-lg p-3 h-64 overflow-y-auto">
            {connectionLogs.length === 0 ? (
              <div className="text-synrgy-muted text-sm">No logs yet...</div>
            ) : (
              <div className="space-y-1">
                {connectionLogs.map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-xs text-synrgy-text font-mono"
                  >
                    {log}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Received Messages */}
        <div>
          <div className="text-sm text-synrgy-muted mb-2">Received Messages</div>
          <div className="bg-synrgy-bg-900/50 rounded-lg p-3 h-64 overflow-y-auto">
            {receivedMessages.length === 0 ? (
              <div className="text-synrgy-muted text-sm">No messages yet...</div>
            ) : (
              <div className="space-y-2">
                {receivedMessages.map((message, index) => (
                  <motion.div
                    key={`${message.id}-${index}`}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-synrgy-primary/5 border border-synrgy-primary/10 rounded p-2"
                  >
                    <div className="text-xs text-synrgy-muted mb-1">
                      {message.role} • {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="text-sm text-synrgy-text line-clamp-3">
                      {message.content}
                    </div>
                    {message.status && (
                      <div className="text-xs text-synrgy-accent mt-1">
                        Status: {message.status}
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
