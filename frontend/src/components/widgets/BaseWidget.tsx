import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MoreHorizontal, 
  Maximize2, 
  Minimize2, 
  Pin, 
  PinOff, 
  MessageSquare, 
  RefreshCw, 
  Settings,
  X,
  ExternalLink
} from 'lucide-react'

import type { DashboardWidget } from '../../types'
import { useHybridStore } from '../../stores/hybridStore'
import SmartContextTrigger from '../Hybrid/SmartContextTrigger'

export interface BaseWidgetProps {
  widget: DashboardWidget
  isExpanded?: boolean
  isPinned?: boolean
  showActions?: boolean
  onExpand?: () => void
  onPin?: () => void
  onUnpin?: () => void
  onRefresh?: () => void
  onSettings?: () => void
  onRemove?: () => void
  onAskSynrgy?: (query: string) => void
  className?: string
  children: React.ReactNode
}

export default function BaseWidget({
  widget,
  isExpanded = false,
  isPinned = false,
  showActions = true,
  onExpand,
  onPin,
  onUnpin,
  onRefresh,
  onSettings,
  onRemove,
  onAskSynrgy,
  className = '',
  children
}: BaseWidgetProps) {
  const [showMenu, setShowMenu] = useState(false)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={`
        bg-synrgy-surface border border-synrgy-primary/20 rounded-xl overflow-hidden
        hover:border-synrgy-primary/40 transition-all duration-200 group
        ${isExpanded ? 'shadow-2xl z-50' : 'shadow-lg'}
        ${className}
      `}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between p-4 border-b border-synrgy-primary/10">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {isPinned && (
              <Pin className="w-3 h-3 text-synrgy-accent" />
            )}
            <h3 className="font-semibold text-synrgy-text truncate">
              {widget.title}
            </h3>
          </div>
          {widget.last_updated && (
            <span className="text-xs text-synrgy-muted">
              Updated {new Date(widget.last_updated).toLocaleTimeString()}
            </span>
          )}
        </div>

        {showActions && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {/* Smart Context Trigger */}
            <SmartContextTrigger
              widget={widget}
              variant="minimal"
              className="text-synrgy-accent hover:bg-synrgy-accent/10"
              onSpawn={(context, query) => {
                // Optional custom handling
                onAskSynrgy?.(query)
              }}
            />

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
              title="Refresh widget data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            {/* Expand/Collapse Button */}
            <button
              onClick={onExpand}
              className="p-1.5 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
              title={isExpanded ? "Minimize" : "Expand"}
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            {/* Pin/Unpin Button */}
            <button
              onClick={isPinned ? onUnpin : onPin}
              className={`p-1.5 rounded-lg transition-colors ${
                isPinned 
                  ? 'text-synrgy-accent hover:bg-synrgy-accent/10' 
                  : 'text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10'
              }`}
              title={isPinned ? "Unpin widget" : "Pin widget"}
            >
              {isPinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
            </button>

            {/* More Actions Menu */}
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-1.5 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
                title="More actions"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>

              <AnimatePresence>
                {showMenu && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 top-full mt-1 bg-synrgy-surface border border-synrgy-primary/20 rounded-lg shadow-xl z-50 min-w-48"
                  >
                    <div className="p-2">
                      <button
                        onClick={() => {
                          setShowMenu(false)
                          onSettings?.()
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg text-synrgy-text hover:bg-synrgy-primary/10 transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                        Widget Settings
                      </button>
                      
                      <button
                        onClick={() => {
                          setShowMenu(false)
                          window.open(`/widget/${widget.id}`, '_blank')
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg text-synrgy-text hover:bg-synrgy-primary/10 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Open in New Tab
                      </button>
                      
                      <div className="my-1 border-t border-synrgy-primary/10" />
                      
                      <button
                        onClick={() => {
                          setShowMenu(false)
                          onRemove?.()
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg text-red-400 hover:bg-red-500/10 transition-colors"
                      >
                        <X className="w-4 h-4" />
                        Remove Widget
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        )}
      </div>

      {/* Widget Content */}
      <div className="relative">
        {children}
      </div>


      {/* Click outside handler */}
      {showMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowMenu(false)}
        />
      )}
    </motion.div>
  )
}
