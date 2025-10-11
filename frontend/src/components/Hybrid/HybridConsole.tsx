import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageSquare,
  LayoutDashboard,
  ArrowLeftRight,
  Pin,
  PinOff
} from 'lucide-react'
import { useLocation } from 'react-router-dom'

import DashboardMain from '@/components/Dashboard/DashboardMain'
import ChatWindow from '@/components/Chat/ChatWindow'
import { useAppStore } from '@/stores/appStore'
import { useChatStore } from '@/stores/chatStore'

interface HybridConsoleProps {
  className?: string
}

export default function HybridConsole({ className = '' }: HybridConsoleProps) {
  const [dashboardWidth, setDashboardWidth] = useState(70) // Percentage
  const [isResizing, setIsResizing] = useState(false)
  const [chatExpanded, setChatExpanded] = useState(false)
  const [dashboardFocused, setDashboardFocused] = useState(false)
  const [pinnedToDashboard, setPinnedToDashboard] = useState(false)
  
  const { chatPanelOpen, setChatPanelOpen } = useAppStore()
  const { sendMessage, context } = useChatStore()
  const location = useLocation()

  // Handle initial query from navigation state
  useEffect(() => {
    const state = location.state as any
    if (state?.query) {
      // Auto-send the query if one was passed from dashboard
      sendMessage({
        query: state.query,
        conversation_id: context?.conversation_id,
        user_context: { source: 'dashboard' },
        filters: {},
        limit: 100
      })
    }
  }, [location.state, sendMessage, context])

  const handleDashboardAskSynrgy = (query: string) => {
    // Auto-send message when dashboard asks SYNRGY
    sendMessage({
      query,
      conversation_id: context?.conversation_id,
      user_context: { source: 'dashboard_widget' },
      filters: {},
      limit: 100
    })
    
    // Ensure chat panel is visible
    setChatPanelOpen(true)
    
    // Temporarily highlight the chat area
    setChatExpanded(true)
    setTimeout(() => setChatExpanded(false), 2000)
  }

  const handleResize = (e: React.MouseEvent) => {
    const startX = e.clientX
    const startWidth = dashboardWidth

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX
      const containerWidth = window.innerWidth
      const deltaPercentage = (deltaX / containerWidth) * 100
      const newWidth = Math.max(30, Math.min(80, startWidth + deltaPercentage))
      setDashboardWidth(newWidth)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    setIsResizing(true)
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const toggleChatVisibility = () => {
    setChatPanelOpen(!chatPanelOpen)
  }

  const focusDashboard = () => {
    setDashboardFocused(true)
    setChatPanelOpen(false)
    setDashboardWidth(95)
  }

  const focusChat = () => {
    setDashboardFocused(false)
    setChatPanelOpen(true)
    setDashboardWidth(30)
  }

  const resetLayout = () => {
    setDashboardFocused(false)
    setChatPanelOpen(true)
    setDashboardWidth(70)
  }

  return (
    <div className={`h-full bg-synrgy-bg-900 relative overflow-hidden ${className}`}>
      {/* Layout Controls */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 bg-synrgy-surface/80 backdrop-blur-md border border-synrgy-primary/20 rounded-full px-4 py-2"
        >
          <button
            onClick={focusDashboard}
            className={`p-2 rounded-lg transition-colors ${
              dashboardFocused
                ? 'bg-synrgy-primary text-synrgy-bg-900'
                : 'hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary'
            }`}
            title="Focus Dashboard"
          >
            <LayoutDashboard className="w-4 h-4" />
          </button>

          <button
            onClick={resetLayout}
            className="p-2 hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary rounded-lg transition-colors"
            title="Hybrid Layout"
          >
            <ArrowLeftRight className="w-4 h-4" />
          </button>

          <button
            onClick={focusChat}
            className={`p-2 rounded-lg transition-colors ${
              !dashboardFocused && chatPanelOpen && dashboardWidth < 50
                ? 'bg-synrgy-primary text-synrgy-bg-900'
                : 'hover:bg-synrgy-primary/10 text-synrgy-muted hover:text-synrgy-primary'
            }`}
            title="Focus Chat"
          >
            <MessageSquare className="w-4 h-4" />
          </button>

          <div className="w-px h-6 bg-synrgy-primary/20 mx-1" />

          <button
            onClick={() => setPinnedToDashboard(!pinnedToDashboard)}
            className={`p-2 rounded-lg transition-colors ${
              pinnedToDashboard
                ? 'bg-synrgy-accent text-synrgy-bg-900'
                : 'hover:bg-synrgy-accent/10 text-synrgy-muted hover:text-synrgy-accent'
            }`}
            title={pinnedToDashboard ? 'Unpin from dashboard' : 'Pin to dashboard'}
          >
            {pinnedToDashboard ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
          </button>
        </motion.div>
      </div>

      {/* Main Content */}
      <div className="flex h-full">
        {/* Dashboard Panel */}
        <motion.div
          animate={{ 
            width: `${dashboardWidth}%`,
            opacity: dashboardFocused ? 1 : 0.95
          }}
          transition={{ type: "spring", damping: 20 }}
          className={`relative bg-synrgy-bg-900 ${
            dashboardFocused ? 'z-10' : 'z-0'
          }`}
        >
          <div className="h-full">
            <DashboardMain 
              onAskSynrgy={handleDashboardAskSynrgy}
              className="h-full"
            />
          </div>

          {/* Dashboard overlay when chat is expanded */}
          <AnimatePresence>
            {chatExpanded && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-synrgy-primary pointer-events-none"
              />
            )}
          </AnimatePresence>
        </motion.div>

        {/* Resize Handle */}
        {chatPanelOpen && !dashboardFocused && (
          <div
            className={`w-1 bg-synrgy-primary/20 hover:bg-synrgy-primary/40 cursor-col-resize transition-colors relative group ${
              isResizing ? 'bg-synrgy-primary/60' : ''
            }`}
            onMouseDown={handleResize}
          >
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-8 bg-synrgy-primary/30 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <div className="w-1 h-4 bg-synrgy-primary rounded-full" />
            </div>
          </div>
        )}

        {/* Chat Panel */}
        <AnimatePresence mode="wait">
          {chatPanelOpen && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ 
                width: `${100 - dashboardWidth}%`, 
                opacity: 1
              }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ type: "spring", damping: 20 }}
              className={`relative bg-synrgy-bg-900 border-l border-synrgy-primary/10 ${
                chatExpanded ? 'z-20' : 'z-10'
              }`}
            >
              <div className="h-full">
                <ChatWindow 
                  showHeader={true}
                  title="SYNRGY Assistant" 
                  className="h-full"
                />
              </div>

              {/* Chat expansion indicator */}
              <AnimatePresence>
                {chatExpanded && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="absolute inset-0 border-2 border-synrgy-primary rounded-lg pointer-events-none"
                  />
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat Toggle Button (when chat is hidden) */}
        {!chatPanelOpen && (
          <motion.button
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            onClick={toggleChatVisibility}
            className="fixed right-6 top-1/2 transform -translate-y-1/2 bg-synrgy-primary text-synrgy-bg-900 p-4 rounded-full shadow-synrgy-glow hover:scale-110 transition-all z-30"
            title="Open SYNRGY Chat"
          >
            <MessageSquare className="w-6 h-6" />
          </motion.button>
        )}
      </div>

      {/* Context Sync Indicator */}
      <AnimatePresence>
        {pinnedToDashboard && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed bottom-6 right-6 bg-synrgy-accent/10 border border-synrgy-accent/30 rounded-lg p-3 z-20"
          >
            <div className="flex items-center gap-2 text-sm text-synrgy-accent">
              <Pin className="w-4 h-4" />
              <span>Synced with Dashboard</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Resize Indicator */}
      {isResizing && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-synrgy-surface border border-synrgy-primary/30 rounded-lg px-4 py-2 z-30">
          <div className="text-sm text-synrgy-text">
            Dashboard: {Math.round(dashboardWidth)}% | Chat: {Math.round(100 - dashboardWidth)}%
          </div>
        </div>
      )}

      {/* Connection Status */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
        <div className="flex items-center gap-2 bg-synrgy-surface/60 backdrop-blur-sm border border-synrgy-primary/20 rounded-full px-4 py-2 text-xs text-synrgy-muted">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>Hybrid Mode Active</span>
          <span>•</span>
          <span>Dashboard ↔ Chat Synced</span>
        </div>
      </div>
    </div>
  )
}
