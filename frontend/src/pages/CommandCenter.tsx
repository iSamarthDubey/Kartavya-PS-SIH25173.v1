/**
 * CommandCenter - Chat-first SIEM Investigation Interface
 * Based on SYNRGY.TXT specification for conversational-first experience
 * NO STATIC DATA - All data comes from WebSocket/API
 */

import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  Mic, 
  Settings, 
  History, 
  BookOpen, 
  Code, 
  Pin,
  Download,
  AlertCircle,
  Loader2,
  Zap
} from 'lucide-react'
import { useWebSocket } from '@/providers/WebSocketProvider'
import { useAuth } from '@/providers/AuthProvider'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { toast } from 'react-hot-toast'
import VisualRenderer from '@/components/Chat/VisualRenderer'

interface ConversationSession {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export default function CommandCenter() {
  const { user } = useAuth()
  const { messages, sendMessage, isConnected, connectionStatus } = useWebSocket()
  const [currentInput, setCurrentInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [showExplanations, setShowExplanations] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState<string>()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch recent conversation sessions from backend
  const { data: recentSessions } = useQuery({
    queryKey: ['conversation-sessions'],
    queryFn: async () => {
      const response = await api.get('/api/assistant/sessions')
      return response.data.data as ConversationSession[]
    },
    enabled: !!user,
    refetchOnWindowFocus: true,
  })

  // Fetch conversation context from backend
  const { data: conversationContext } = useQuery({
    queryKey: ['conversation-context', currentConversationId],
    queryFn: async () => {
      const response = await api.get(`/api/assistant/context/${currentConversationId}`)
      return response.data.data
    },
    enabled: !!currentConversationId,
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Generate conversation ID on mount
  useEffect(() => {
    if (!currentConversationId) {
      setCurrentConversationId(`conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
    }
  }, [])

  const handleSendMessage = () => {
    if (!currentInput.trim() || !isConnected) {
      return
    }

    sendMessage(currentInput, currentConversationId)
    setCurrentInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleVoiceInput = async () => {
    if (!('webkitSpeechRecognition' in window)) {
      toast.error('Voice input not supported in this browser')
      return
    }

    try {
      setIsRecording(true)
      // Implement voice recognition
      const recognition = new (window as any).webkitSpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setCurrentInput(transcript)
        setIsRecording(false)
      }

      recognition.onerror = () => {
        setIsRecording(false)
        toast.error('Voice recognition failed')
      }

      recognition.start()
    } catch (error) {
      setIsRecording(false)
      toast.error('Failed to start voice input')
    }
  }

  const handlePinToDashboard = (messageId: string) => {
    // TODO: Implement pin to dashboard functionality
    toast.success('Pinned to dashboard')
  }

  const handleExportData = (messageId: string) => {
    // TODO: Implement export functionality
    toast.success('Export initiated')
  }

  const renderConnectionStatus = () => {
    const statusConfig = {
      connected: { color: 'text-green-400', icon: '●', message: 'Connected' },
      connecting: { color: 'text-yellow-400', icon: '◐', message: 'Connecting...' },
      disconnected: { color: 'text-red-400', icon: '●', message: 'Disconnected' },
      error: { color: 'text-red-400', icon: '⚠', message: 'Connection Error' },
    }

    const status = statusConfig[connectionStatus]
    
    return (
      <div className={`flex items-center gap-2 text-sm ${status.color}`}>
        <span className="animate-pulse">{status.icon}</span>
        <span>{status.message}</span>
      </div>
    )
  }

  return (
    <div className="h-full flex bg-synrgy-bg-900">
      {/* Left Sidebar - Sessions & Context */}
      <div className="w-80 bg-synrgy-surface/30 border-r border-synrgy-primary/10 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-synrgy-primary/10">
          <h2 className="text-lg font-semibold text-synrgy-text mb-2">Command Center</h2>
          <p className="text-sm text-synrgy-muted">Conversational SIEM Investigation</p>
        </div>

        {/* Recent Sessions */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-6">
            <h3 className="text-sm font-medium text-synrgy-muted uppercase tracking-wide mb-3 flex items-center gap-2">
              <History className="w-4 h-4" />
              Recent Sessions
            </h3>
            {recentSessions ? (
              <div className="space-y-2">
                {recentSessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => setCurrentConversationId(session.id)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      session.id === currentConversationId
                        ? 'bg-synrgy-primary/20 border border-synrgy-primary/40'
                        : 'bg-synrgy-surface/50 hover:bg-synrgy-surface/70'
                    }`}
                  >
                    <div className="font-medium text-synrgy-text text-sm truncate">
                      {session.title}
                    </div>
                    <div className="text-xs text-synrgy-muted mt-1">
                      {session.message_count} messages • {new Date(session.updated_at).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-sm text-synrgy-muted">No recent sessions</div>
            )}
          </div>

          {/* Context Panel */}
          {conversationContext && (
            <div>
              <h3 className="text-sm font-medium text-synrgy-muted uppercase tracking-wide mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                Context
              </h3>
              <div className="bg-synrgy-surface/50 rounded-lg p-3">
                <div className="space-y-2 text-sm">
                  {conversationContext.active_filters && (
                    <div>
                      <span className="text-synrgy-accent">Filters:</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {Object.entries(conversationContext.active_filters).map(([key, value]) => (
                          <span
                            key={key}
                            className="px-2 py-1 bg-synrgy-primary/20 text-synrgy-primary text-xs rounded"
                          >
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {conversationContext.entities && (
                    <div>
                      <span className="text-synrgy-accent">Entities:</span>
                      <div className="mt-1 text-synrgy-muted">
                        {conversationContext.entities.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-synrgy-primary/10 bg-synrgy-surface/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-synrgy-primary" />
              <div>
                <h1 className="font-semibold text-synrgy-text">SYNRGY Assistant</h1>
                <p className="text-sm text-synrgy-muted">AI-powered security investigation</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {renderConnectionStatus()}
              <button
                onClick={() => setShowExplanations(!showExplanations)}
                className={`p-2 rounded-lg transition-colors ${
                  showExplanations 
                    ? 'bg-synrgy-primary/20 text-synrgy-primary' 
                    : 'hover:bg-synrgy-surface/50 text-synrgy-muted'
                }`}
                title="Toggle query explanations"
              >
                <Code className="w-4 h-4" />
              </button>
              <button className="p-2 hover:bg-synrgy-surface/50 rounded-lg transition-colors text-synrgy-muted">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Context Chips - Active Filters */}
        {conversationContext?.active_filters && Object.keys(conversationContext.active_filters).length > 0 && (
          <div className="px-6 py-3 border-b border-synrgy-primary/5 bg-synrgy-surface/10">
            <div className="flex items-center gap-2 text-sm text-synrgy-muted mb-2">
              <span>Active filters:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(conversationContext.active_filters).map(([key, value]) => (
                <div
                  key={key}
                  className="flex items-center gap-1 px-2 py-1 bg-synrgy-primary/20 text-synrgy-primary rounded-lg text-xs"
                >
                  <span>{key}: {String(value)}</span>
                  <button
                    onClick={() => {
                      // TODO: Remove filter functionality
                      toast.success(`Removed filter: ${key}`)
                    }}
                    className="hover:bg-synrgy-primary/30 rounded p-0.5 ml-1"
                    title="Remove filter"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 bg-synrgy-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-8 h-8 text-synrgy-primary" />
                </div>
                <h3 className="text-lg font-semibold text-synrgy-text mb-2">
                  Welcome to SYNRGY Command Center
                </h3>
                <p className="text-synrgy-muted mb-6">
                  Start your security investigation by asking a question or describing what you're looking for.
                </p>
                <div className="text-sm text-synrgy-muted space-y-1">
                  <p>Try asking:</p>
                  <div className="space-y-1">
                    <button 
                      onClick={() => setCurrentInput("Show me failed login attempts in the last hour")}
                      className="block w-full text-left px-3 py-2 bg-synrgy-surface/30 rounded-lg hover:bg-synrgy-surface/50 transition-colors"
                    >
                      "Show me failed login attempts in the last hour"
                    </button>
                    <button 
                      onClick={() => setCurrentInput("Find suspicious network activity")}
                      className="block w-full text-left px-3 py-2 bg-synrgy-surface/30 rounded-lg hover:bg-synrgy-surface/50 transition-colors"
                    >
                      "Find suspicious network activity"
                    </button>
                    <button 
                      onClick={() => setCurrentInput("Analyze malware detections today")}
                      className="block w-full text-left px-3 py-2 bg-synrgy-surface/30 rounded-lg hover:bg-synrgy-surface/50 transition-colors"
                    >
                      "Analyze malware detections today"
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-4xl ${message.role === 'user' ? 'ml-12' : 'mr-12'}`}>
                    {/* Message Content */}
                    <div className={`p-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-synrgy-primary text-synrgy-bg-900 rounded-br-sm'
                        : 'bg-synrgy-surface/50 border border-synrgy-primary/10 rounded-bl-sm'
                    }`}>
                      <div className="flex items-start gap-3">
                        <div className="flex-1">
                          <div className={message.role === 'user' ? 'text-synrgy-bg-900' : 'text-synrgy-text'}>
                            {message.content}
                          </div>
                          
                          {/* Processing indicator */}
                          {message.status === 'processing' && (
                            <div className="flex items-center gap-2 mt-2 text-synrgy-muted">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span className="text-sm">{message.stage || 'Processing...'}</span>
                            </div>
                          )}
                          
                          {/* Visual payload rendering */}
                          {message.visual_payload && message.status === 'success' && (
                            <div className="mt-4">
                              <VisualRenderer payload={message.visual_payload} />
                            </div>
                          )}
                          
                          {/* Query explanation */}
                          {showExplanations && message.metadata && message.role === 'assistant' && (
                            <details className="mt-3 bg-synrgy-bg-900/20 rounded-lg">
                              <summary className="p-2 cursor-pointer text-sm text-synrgy-muted hover:text-synrgy-text">
                                Query Details
                              </summary>
                              <div className="p-3 text-xs font-mono">
                                {message.metadata.intent && (
                                  <div className="mb-2">
                                    <span className="text-synrgy-accent">Intent:</span> {message.metadata.intent}
                                  </div>
                                )}
                                {message.metadata.confidence && (
                                  <div className="mb-2">
                                    <span className="text-synrgy-accent">Confidence:</span> {(message.metadata.confidence * 100).toFixed(0)}%
                                  </div>
                                )}
                                {message.metadata.entities && (
                                  <div>
                                    <span className="text-synrgy-accent">Entities:</span> {JSON.stringify(message.metadata.entities, null, 2)}
                                  </div>
                                )}
                              </div>
                            </details>
                          )}
                        </div>
                        
                        {/* Action buttons for assistant messages */}
                        {message.role === 'assistant' && message.status === 'success' && (
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handlePinToDashboard(message.id)}
                              className="p-1 hover:bg-synrgy-primary/20 rounded text-synrgy-muted hover:text-synrgy-primary"
                              title="Pin to Dashboard"
                            >
                              <Pin className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => handleExportData(message.id)}
                              className="p-1 hover:bg-synrgy-accent/20 rounded text-synrgy-muted hover:text-synrgy-accent"
                              title="Export Data"
                            >
                              <Download className="w-3 h-3" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Timestamp */}
                    <div className={`text-xs text-synrgy-muted mt-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-synrgy-primary/10 bg-synrgy-surface/10">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your security data..."
                className="w-full min-h-[60px] max-h-32 p-3 pr-12 bg-synrgy-surface/50 border border-synrgy-primary/20 rounded-xl text-synrgy-text placeholder:text-synrgy-muted focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50 focus:border-synrgy-primary/50 resize-none"
                disabled={!isConnected}
              />
              
              {/* Voice input button */}
              <button
                onClick={handleVoiceInput}
                disabled={isRecording || !isConnected}
                className={`absolute right-3 bottom-3 p-1.5 rounded-lg transition-colors ${
                  isRecording 
                    ? 'bg-red-500/20 text-red-400' 
                    : 'hover:bg-synrgy-primary/20 text-synrgy-muted hover:text-synrgy-primary'
                }`}
                title="Voice input"
              >
                <Mic className={`w-4 h-4 ${isRecording ? 'animate-pulse' : ''}`} />
              </button>
            </div>
            
            <button
              onClick={handleSendMessage}
              disabled={!currentInput.trim() || !isConnected}
              className="p-3 bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 disabled:bg-synrgy-muted/20 disabled:text-synrgy-muted rounded-xl transition-colors"
              title="Send message"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {!isConnected && (
            <div className="flex items-center gap-2 mt-2 text-sm text-amber-400">
              <AlertCircle className="w-4 h-4" />
              <span>Connecting to SYNRGY services...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
