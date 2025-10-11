import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageSquare, 
  LayoutDashboard, 
  Maximize2, 
  Minimize2, 
  Settings, 
  RefreshCcw,
  SplitSquareHorizontal,
  PanelLeftClose,
  PanelLeftOpen
} from 'lucide-react'

import { useHybridStore, useHybridMode } from '../../stores/hybridStore'
import { useChatStore } from '../../stores/chatStore'
import ChatWindow from '../Chat/ChatWindow'
import DashboardMain from '../Dashboard/DashboardMain'
import ContextBridge from './ContextBridge'

interface HybridLayoutProps {
  className?: string
}

export default function HybridLayout({ className = '' }: HybridLayoutProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [dragStartX, setDragStartX] = useState(0)
  
  const {
    isHybridMode,
    layout,
    splitRatio,
    chatPanelCollapsed,
    setSplitRatio,
    setLayout,
    toggleChatPanel,
    spawnChatFromWidget,
    syncContexts
  } = useHybridStore()
  
  const { isLoading: chatLoading } = useChatStore()

  // Handle split pane dragging
  const handleDragStart = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStartX(e.clientX)
    e.preventDefault()
  }

  const handleDragMove = (e: MouseEvent) => {
    if (!isDragging) return
    
    const container = document.querySelector('.hybrid-container')
    if (!container) return
    
    const containerRect = container.getBoundingClientRect()
    const newRatio = (e.clientX - containerRect.left) / containerRect.width
    const clampedRatio = Math.max(0.2, Math.min(0.8, newRatio))
    
    setSplitRatio(clampedRatio)
  }

  const handleDragEnd = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDragMove)
      document.addEventListener('mouseup', handleDragEnd)
      document.body.style.userSelect = 'none'
      document.body.style.cursor = 'col-resize'
      
      return () => {
        document.removeEventListener('mousemove', handleDragMove)
        document.removeEventListener('mouseup', handleDragEnd)
        document.body.style.userSelect = ''
        document.body.style.cursor = ''
      }
    }
  }, [isDragging])

  // Render layout controls
  const renderLayoutControls = () => (
    <div className="flex items-center gap-2 p-3 bg-synrgy-surface/50 border-b border-synrgy-primary/10">
      <div className="flex items-center gap-1 mr-4">
        <button
          onClick={() => setLayout('dashboard-only')}
          className={`p-2 rounded-lg transition-all ${
            layout === 'dashboard-only' 
              ? 'bg-synrgy-primary/20 text-synrgy-primary' 
              : 'text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10'
          }`}
          title="Dashboard only"
        >
          <LayoutDashboard className="w-4 h-4" />
        </button>
        
        <button
          onClick={() => setLayout('split-view')}
          className={`p-2 rounded-lg transition-all ${
            layout === 'split-view' 
              ? 'bg-synrgy-primary/20 text-synrgy-primary' 
              : 'text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10'
          }`}
          title="Split view"
        >
          <SplitSquareHorizontal className="w-4 h-4" />
        </button>
        
        <button
          onClick={() => setLayout('chat-only')}
          className={`p-2 rounded-lg transition-all ${
            layout === 'chat-only' 
              ? 'bg-synrgy-primary/20 text-synrgy-primary' 
              : 'text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10'
          }`}
          title="Chat only"
        >
          <MessageSquare className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex items-center gap-1 mr-4">
        <button
          onClick={toggleChatPanel}
          className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-all"
          title={chatPanelCollapsed ? "Show chat panel" : "Hide chat panel"}
        >
          {chatPanelCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
        </button>
        
        <button
          onClick={syncContexts}
          className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-accent hover:bg-synrgy-accent/10 transition-all"
          title="Sync contexts"
        >
          <RefreshCcw className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex items-center gap-2 text-xs text-synrgy-muted">
        <span>Hybrid Mode</span>
        <div className={`w-2 h-2 rounded-full ${chatLoading ? 'bg-synrgy-accent animate-pulse' : 'bg-green-500'}`} />
      </div>
      
      {/* Context Bridge - Compact Mode */}
      <ContextBridge 
        showCompact={true} 
        className="ml-4"
      />
      
      <div className="ml-auto">
        <button className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-all">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </div>
  )

  // Render split view
  const renderSplitView = () => (
    <div className="hybrid-container flex-1 flex overflow-hidden">
      {/* Dashboard Section */}
      <motion.div
        initial={false}
        animate={{ 
          width: `${splitRatio * 100}%`,
          opacity: splitRatio > 0.1 ? 1 : 0
        }}
        className="flex flex-col border-r border-synrgy-primary/10 bg-synrgy-bg-900"
      >
        <div className="flex-1 overflow-hidden">
          <DashboardMain 
            className="h-full"
            hybridMode={true}
            onWidgetAction={(widgetId, action, data) => {
              if (action === 'ask_synrgy') {
                spawnChatFromWidget(widgetId, data.query)
              }
            }}
          />
        </div>
      </motion.div>

      {/* Draggable Divider */}
      <div
        className={`w-1 bg-synrgy-primary/20 hover:bg-synrgy-primary/40 cursor-col-resize transition-colors ${
          isDragging ? 'bg-synrgy-primary/60' : ''
        }`}
        onMouseDown={handleDragStart}
      >
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-0.5 h-8 bg-synrgy-primary/60 rounded-full" />
        </div>
      </div>

      {/* Chat Section */}
      <AnimatePresence>
        {!chatPanelCollapsed && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ 
              width: `${(1 - splitRatio) * 100}%`,
              opacity: (1 - splitRatio) > 0.1 ? 1 : 0
            }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="flex flex-col bg-synrgy-bg-900"
          >
            <div className="flex-1 overflow-hidden">
              <ChatWindow 
                className="h-full"
                showHeader={true}
                title="SYNRGY Assistant"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )

  // Render overlay view
  const renderOverlayView = () => (
    <div className="relative flex-1 overflow-hidden">
      {/* Dashboard Background */}
      <div className="absolute inset-0">
        <DashboardMain 
          className="h-full"
          hybridMode={true}
          onWidgetAction={(widgetId, action, data) => {
            if (action === 'ask_synrgy') {
              spawnChatFromWidget(widgetId, data.query)
            }
          }}
        />
      </div>

      {/* Chat Overlay */}
      <AnimatePresence>
        {!chatPanelCollapsed && (
          <motion.div
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="absolute top-0 right-0 w-96 h-full bg-synrgy-surface border-l border-synrgy-primary/20 shadow-2xl z-50"
          >
            <ChatWindow 
              className="h-full"
              showHeader={true}
              title="SYNRGY Assistant"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )

  // Render single pane view
  const renderSingleView = (type: 'dashboard' | 'chat') => (
    <div className="flex-1 overflow-hidden">
      {type === 'dashboard' ? (
        <DashboardMain 
          className="h-full"
          hybridMode={false}
          onWidgetAction={(widgetId, action, data) => {
            if (action === 'ask_synrgy') {
              // Switch to hybrid mode and spawn chat
              setLayout('split-view')
              setTimeout(() => spawnChatFromWidget(widgetId, data.query), 300)
            }
          }}
        />
      ) : (
        <ChatWindow 
          className="h-full"
          showHeader={true}
          title="SYNRGY Assistant"
        />
      )}
    </div>
  )

  // Main render
  if (!isHybridMode && layout !== 'chat-only' && layout !== 'dashboard-only') {
    return renderSingleView('dashboard')
  }

  return (
    <motion.div 
      className={`flex flex-col h-full bg-synrgy-bg-900 ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Layout Controls */}
      {renderLayoutControls()}

      {/* Main Content Area */}
      {layout === 'split-view' && renderSplitView()}
      {layout === 'overlay' && renderOverlayView()}
      {layout === 'dashboard-only' && renderSingleView('dashboard')}
      {layout === 'chat-only' && renderSingleView('chat')}

      {/* Global Loading Overlay */}
      <AnimatePresence>
        {chatLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-synrgy-bg-900/80 flex items-center justify-center z-50 pointer-events-none"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border-2 border-synrgy-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-synrgy-text">Processing...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
