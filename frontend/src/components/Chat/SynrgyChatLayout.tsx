/**
 * SYNRGY Complete Chat Layout
 * Integrated chat system with all enhanced features
 */

import React, { useState, useRef, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageSquare, 
  Settings, 
  MoreVertical, 
  Minimize2, 
  Maximize2,
  X,
  Volume2,
  VolumeX,
  Palette,
  Moon,
  Sun,
  Zap,
  Shield,
  History,
  BookOpen,
  Star,
  Download,
  Upload,
  RefreshCw,
  Sidebar,
  PanelLeftClose,
  PanelLeftOpen,
  Command as CommandIcon
} from 'lucide-react'

import { 
  EnhancedChatInterface,
  CommandSuggestions, 
  ConversationContext 
} from '@/components/Chat'
import EnhancedChatInput from '@/components/Chat/EnhancedChatInput'
import { 
  TouchButton, 
  useToast, 
  ResponsiveContainer,
  AnimatedCard,
  useBreakpoint,
  Tooltip,
  LoadingSpinner
} from '@/components/UI'
import { useWebSocketStream } from '@/hooks/useWebSocketStream'
import { useChatHistory } from '@/hooks/useChatHistory'
import type { ChatMessage, VisualPayload } from '@/types'

interface ChatLayoutProps {
  className?: string
  onClose?: () => void
  defaultMinimized?: boolean
  showSidebar?: boolean
}

interface ChatSettings {
  theme: 'auto' | 'light' | 'dark'
  soundEnabled: boolean
  autoScroll: boolean
  showTimestamps: boolean
  compactMode: boolean
  visualizations: boolean
}

// Main Chat Layout Component
export const SynrgyChatLayout: React.FC<ChatLayoutProps> = ({
  className = '',
  onClose,
  defaultMinimized = false,
  showSidebar = true
}) => {
  const [isMinimized, setIsMinimized] = useState(defaultMinimized)
  const [showSettings, setShowSettings] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [currentSession, setCurrentSession] = useState<string>('')
  const [chatSettings, setChatSettings] = useState<ChatSettings>({
    theme: 'auto',
    soundEnabled: true,
    autoScroll: true,
    showTimestamps: true,
    compactMode: false,
    visualizations: true
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [showCommandPanel, setShowCommandPanel] = useState(false)

  const { showToast } = useToast()
  const { isMobile, isTablet } = useBreakpoint()
  
  // Chat hooks
  const {
    messages,
    isLoading,
    isTyping,
    sendMessage,
    clearHistory,
    searchMessages,
    exportChat,
    importChat
  } = useChatHistory()

  const {
    connect,
    disconnect,
    isConnected,
    connectionStatus,
    sendStreamMessage
  } = useWebSocketStream({
    url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/chat',
    onMessage: (data) => {
      // Handle streaming response
      console.log('Received stream data:', data)
    },
    onError: (error) => {
      showToast({
        type: 'error',
        title: 'Connection Error',
        message: 'Failed to connect to chat service'
      })
    }
  })

  // Auto-connect WebSocket
  useEffect(() => {
    if (!isConnected) {
      connect()
    }
    return () => disconnect()
  }, [connect, disconnect, isConnected])

  // Handle message sending
  const handleSendMessage = async (message: string, attachments?: File[], metadata?: any) => {
    try {
      // Send via WebSocket if connected, otherwise use HTTP
      if (isConnected) {
        await sendStreamMessage({
          content: message,
          attachments: attachments?.map(f => ({ name: f.name, size: f.size, type: f.type })),
          metadata,
          session_id: currentSession
        })
      } else {
        await sendMessage(message, attachments, metadata)
      }

      // Play sound if enabled
      if (chatSettings.soundEnabled) {
        // Play send sound
        const audio = new Audio('/sounds/message-send.mp3')
        audio.play().catch(() => {}) // Ignore errors
      }

    } catch (error) {
      showToast({
        type: 'error',
        title: 'Send Failed',
        message: 'Unable to send message. Please try again.'
      })
    }
  }

  // Handle voice input
  const handleVoiceInput = async (audioBlob: Blob) => {
    try {
      // Convert audio to text and send as message
      // This would integrate with speech-to-text service
      showToast({
        type: 'info',
        title: 'Processing...',
        message: 'Converting speech to text'
      })
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Voice Input Failed',
        message: 'Unable to process voice input'
      })
    }
  }

  // Sidebar content based on current view
  const renderSidebarContent = () => {
    if (showCommandPanel) {
      return (
        <CommandSuggestions
          onSelectCommand={(command) => {
            // Set command in input
            setShowCommandPanel(false)
          }}
          currentInput=""
          recentCommands={[]}
          className="h-full"
        />
      )
    }

    return (
      <div className="h-full flex flex-col">
        {/* Session Info */}
        <div className="p-4 border-b border-synrgy-primary/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center">
              <Shield className="w-4 h-4 text-synrgy-bg-900" />
            </div>
            <div>
              <p className="font-semibold text-synrgy-text text-sm">Active Session</p>
              <p className="text-xs text-synrgy-muted">
                {isConnected ? 'Connected' : 'Disconnected'}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="p-4 space-y-2">
          <TouchButton
            variant="ghost"
            className="w-full justify-start"
            onClick={() => setShowCommandPanel(true)}
          >
            <CommandIcon className="w-4 h-4 mr-2" />
            Commands
          </TouchButton>
          
          <TouchButton
            variant="ghost"
            className="w-full justify-start"
            onClick={() => {/* Show history */}}
          >
            <History className="w-4 h-4 mr-2" />
            History
          </TouchButton>
          
          <TouchButton
            variant="ghost"
            className="w-full justify-start"
            onClick={() => {/* Show bookmarks */}}
          >
            <Star className="w-4 h-4 mr-2" />
            Bookmarks
          </TouchButton>
          
          <TouchButton
            variant="ghost"
            className="w-full justify-start"
            onClick={() => {/* Show help */}}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Help & Tips
          </TouchButton>
        </div>

        {/* Recent Sessions */}
        <div className="p-4 flex-1">
          <h4 className="text-sm font-medium text-synrgy-muted mb-2">Recent Sessions</h4>
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <TouchButton
                key={i}
                variant="ghost"
                className="w-full justify-start text-xs p-2"
              >
                <MessageSquare className="w-3 h-3 mr-2" />
                Session {i}
              </TouchButton>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className="p-4 border-t border-synrgy-primary/10">
          <TouchButton
            variant="ghost"
            className="w-full justify-start"
            onClick={() => setShowSettings(true)}
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </TouchButton>
        </div>
      </div>
    )
  }

  // Settings Panel
  const SettingsPanel = () => (
    <AnimatedCard className="absolute inset-4 z-50 bg-synrgy-surface border border-synrgy-primary/20 max-w-md mx-auto">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-synrgy-text">Chat Settings</h3>
          <TouchButton
            variant="ghost"
            size="sm"
            onClick={() => setShowSettings(false)}
          >
            <X className="w-4 h-4" />
          </TouchButton>
        </div>

        <div className="space-y-4">
          {/* Theme */}
          <div>
            <label className="text-sm font-medium text-synrgy-text mb-2 block">Theme</label>
            <div className="flex gap-2">
              {[
                { value: 'light', icon: Sun, label: 'Light' },
                { value: 'dark', icon: Moon, label: 'Dark' },
                { value: 'auto', icon: Palette, label: 'Auto' }
              ].map(theme => (
                <TouchButton
                  key={theme.value}
                  variant={chatSettings.theme === theme.value ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setChatSettings(prev => ({ ...prev, theme: theme.value as any }))}
                  className="flex-1"
                >
                  <theme.icon className="w-3 h-3 mr-1" />
                  {theme.label}
                </TouchButton>
              ))}
            </div>
          </div>

          {/* Sound */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-synrgy-text">Sound Effects</span>
            <TouchButton
              variant="ghost"
              size="sm"
              onClick={() => setChatSettings(prev => ({ ...prev, soundEnabled: !prev.soundEnabled }))}
            >
              {chatSettings.soundEnabled ? (
                <Volume2 className="w-4 h-4 text-synrgy-primary" />
              ) : (
                <VolumeX className="w-4 h-4 text-synrgy-muted" />
              )}
            </TouchButton>
          </div>

          {/* Other settings */}
          {[
            { key: 'autoScroll', label: 'Auto Scroll' },
            { key: 'showTimestamps', label: 'Show Timestamps' },
            { key: 'compactMode', label: 'Compact Mode' },
            { key: 'visualizations', label: 'Enable Visualizations' }
          ].map(setting => (
            <div key={setting.key} className="flex items-center justify-between">
              <span className="text-sm font-medium text-synrgy-text">{setting.label}</span>
              <TouchButton
                variant={chatSettings[setting.key as keyof ChatSettings] ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setChatSettings(prev => ({ 
                  ...prev, 
                  [setting.key]: !prev[setting.key as keyof ChatSettings] 
                }))}
              >
                {chatSettings[setting.key as keyof ChatSettings] ? '✓' : '○'}
              </TouchButton>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <TouchButton
            variant="ghost"
            className="flex-1"
            onClick={() => exportChat()}
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </TouchButton>
          
          <TouchButton
            variant="ghost"
            className="flex-1"
            onClick={() => {/* Import */}}
          >
            <Upload className="w-4 h-4 mr-2" />
            Import
          </TouchButton>
          
          <TouchButton
            variant="outline"
            className="flex-1"
            onClick={() => clearHistory()}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Clear
          </TouchButton>
        </div>
      </div>
    </AnimatedCard>
  )

  if (isMinimized) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`fixed bottom-4 right-4 z-40 ${className}`}
      >
        <TouchButton
          variant="primary"
          onClick={() => setIsMinimized(false)}
          className="w-14 h-14 rounded-full shadow-xl"
        >
          <MessageSquare className="w-6 h-6" />
        </TouchButton>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        fixed inset-4 z-30 max-w-7xl mx-auto
        ${isMobile ? 'inset-2' : ''}
        ${className}
      `}
    >
      <AnimatedCard className="h-full flex bg-synrgy-bg-950 border border-synrgy-primary/20 shadow-2xl">
        {/* Sidebar */}
        <AnimatePresence>
          {showSidebar && !sidebarCollapsed && !isMobile && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 320, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="flex-shrink-0 bg-synrgy-surface/30 border-r border-synrgy-primary/10 overflow-hidden"
            >
              {renderSidebarContent()}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <div className="flex-shrink-0 flex items-center justify-between p-4 border-b border-synrgy-primary/10 bg-synrgy-surface/20">
            <div className="flex items-center gap-3">
              {showSidebar && !isMobile && (
                <TouchButton
                  variant="ghost"
                  size="sm"
                  onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                >
                  {sidebarCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
                </TouchButton>
              )}
              
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent flex items-center justify-center">
                  <Zap className="w-4 h-4 text-synrgy-bg-900" />
                </div>
                <div>
                  <h2 className="font-semibold text-synrgy-text">SYNRGY Assistant</h2>
                  {isConnected && (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-xs text-synrgy-muted">Live</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {!isMobile && (
                <TouchButton
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSettings(true)}
                >
                  <Settings className="w-4 h-4" />
                </TouchButton>
              )}

              <TouchButton
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(true)}
              >
                <Minimize2 className="w-4 h-4" />
              </TouchButton>

              {onClose && (
                <TouchButton
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                >
                  <X className="w-4 h-4" />
                </TouchButton>
              )}
            </div>
          </div>

          {/* Chat Interface */}
          <div className="flex-1 flex flex-col min-h-0 relative">
            <EnhancedChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              onVoiceInput={handleVoiceInput}
              isLoading={isLoading}
              isTyping={isTyping}
              className="flex-1"
            />

            {/* Contextual Follow-ups */}
            {messages.length > 0 && (
              <div className="p-4 border-t border-synrgy-primary/10 bg-synrgy-surface/20">
                <ConversationContext
                  lastMessage={messages[messages.length - 1]}
                  sessionTopic={currentSession}
                  onFollowup={handleSendMessage}
                />
              </div>
            )}
          </div>
        </div>

        {/* Settings Overlay */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-synrgy-bg-950/80 backdrop-blur-sm flex items-center justify-center z-50"
              onClick={() => setShowSettings(false)}
            >
              <div onClick={e => e.stopPropagation()}>
                <SettingsPanel />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </AnimatedCard>
    </motion.div>
  )
}

// Floating Chat Button (for embedding in other pages)
export const FloatingChatButton: React.FC<{
  onClick: () => void
  isActive?: boolean
  hasUnread?: boolean
}> = ({ 
  onClick, 
  isActive = false,
  hasUnread = false 
}) => {
  return (
    <motion.div
      className="fixed bottom-6 right-6 z-30"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <TouchButton
        variant="primary"
        onClick={onClick}
        className={`
          w-14 h-14 rounded-full shadow-xl relative
          ${isActive ? 'bg-synrgy-accent' : ''}
        `}
      >
        <MessageSquare className="w-6 h-6" />
        
        {hasUnread && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-xs text-white">!</span>
          </div>
        )}
      </TouchButton>
    </motion.div>
  )
}

export default SynrgyChatLayout
