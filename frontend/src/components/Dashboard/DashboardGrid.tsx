import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Grid3X3, 
  Plus, 
  LayoutDashboard, 
  Trash2, 
  RotateCcw,
  Maximize2,
  Settings
} from 'lucide-react'

import { useHybridStore, useWidgetManagement } from '../../stores/hybridStore'
import VisualRenderer from '@/components/Visuals/VisualRenderer'
import ChartWidget from '../widgets/ChartWidget'
import SummaryCardWidget from '../widgets/SummaryCardWidget'
import BaseWidget from '../widgets/BaseWidget'
import type { DashboardWidget, VisualPayload, SummaryCard } from '../../types'

interface DashboardGridProps {
  hybridMode?: boolean
  onWidgetAction?: (widgetId: string, action: string, data?: any) => void
  className?: string
}

export default function DashboardGrid({ 
  hybridMode = false, 
  onWidgetAction,
  className = '' 
}: DashboardGridProps) {
  const [expandedWidget, setExpandedWidget] = useState<string | null>(null)
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null)
  
  const { 
    pinnedWidgets, 
    widgetLayout,
    pinWidget,
    unpinWidget,
    updateWidgetPosition,
    clearAllWidgets,
    optimizeLayout
  } = useWidgetManagement()

  // Handle widget expansion
  const handleExpand = useCallback((widgetId: string) => {
    setExpandedWidget(expandedWidget === widgetId ? null : widgetId)
  }, [expandedWidget])

  // Handle widget pinning
  const handlePin = useCallback((widget: DashboardWidget) => {
    pinWidget(widget)
    onWidgetAction?.(widget.id, 'pin', { widget })
  }, [pinWidget, onWidgetAction])

  // Handle widget unpinning
  const handleUnpin = useCallback((widgetId: string) => {
    unpinWidget(widgetId)
    onWidgetAction?.(widgetId, 'unpin')
  }, [unpinWidget, onWidgetAction])

  // Handle widget refresh
  const handleRefresh = useCallback(async (widgetId: string) => {
    // Simulate refresh - in real app, this would call API
    const widget = pinnedWidgets.find(w => w.id === widgetId)
    if (widget) {
      const updatedWidget = {
        ...widget,
        last_updated: new Date().toISOString()
      }
      pinWidget(updatedWidget)
      onWidgetAction?.(widgetId, 'refresh', { widget: updatedWidget })
    }
  }, [pinnedWidgets, pinWidget, onWidgetAction])

  // Handle Ask SYNRGY from widget
  const handleAskSynrgy = useCallback((widgetId: string, query: string) => {
    onWidgetAction?.(widgetId, 'ask_synrgy', { query })
  }, [onWidgetAction])

  // Handle widget removal
  const handleRemove = useCallback((widgetId: string) => {
    handleUnpin(widgetId)
    onWidgetAction?.(widgetId, 'remove')
  }, [handleUnpin, onWidgetAction])

  // Handle widget settings
  const handleSettings = useCallback((widgetId: string) => {
    onWidgetAction?.(widgetId, 'settings')
  }, [onWidgetAction])

  // Render widget using VisualRenderer for consistency
  const renderWidget = (widget: DashboardWidget) => {
    // Convert widget data to visual payload if needed
    const payload = widget.data && typeof widget.data === 'object' && 'type' in widget.data 
      ? widget.data as VisualPayload
      : {
          type: widget.type,
          title: widget.title,
          description: widget.description || `${widget.type} widget`,
          data: widget.data
        }

    return (
      <VisualRenderer
        payload={payload}
        messageId={widget.id}
        conversationId="dashboard"
        onAskSynrgy={onWidgetAction ? (query: string) => handleAskSynrgy(widget.id, query) : undefined}
        showActions={true}
        compact={expandedWidget !== widget.id}
        actions={[
          {
            label: expandedWidget === widget.id ? 'Collapse' : 'Expand',
            icon: 'maximize',
            action: () => handleExpand(widget.id)
          },
          {
            label: 'Refresh',
            icon: 'refresh',
            action: () => handleRefresh(widget.id)
          },
          {
            label: 'Settings',
            icon: 'settings',
            action: () => handleSettings(widget.id)
          },
          {
            label: 'Remove',
            icon: 'trash',
            action: () => handleRemove(widget.id)
          }
        ]}
      />
    )
  }

  // Get grid layout classes based on number of widgets
  const getGridLayout = () => {
    const count = pinnedWidgets.length
    
    if (count === 0) return 'grid-cols-1'
    if (count === 1) return 'grid-cols-1'
    if (count === 2) return 'grid-cols-1 lg:grid-cols-2'
    if (count <= 4) return 'grid-cols-1 md:grid-cols-2'
    if (count <= 6) return 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
    return 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4'
  }

  if (pinnedWidgets.length === 0) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md"
        >
          <div className="w-20 h-20 mx-auto mb-6 bg-synrgy-primary/10 rounded-full flex items-center justify-center">
            <Grid3X3 className="w-10 h-10 text-synrgy-primary" />
          </div>
          
          <h3 className="text-xl font-semibold text-synrgy-text mb-3">
            No Pinned Widgets
          </h3>
          
          <p className="text-synrgy-muted mb-6 leading-relaxed">
            {hybridMode 
              ? "Start a conversation with SYNRGY and pin visualizations to build your custom dashboard."
              : "Pin charts, metrics, and insights from chat responses to create your personalized security dashboard."
            }
          </p>
          
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => onWidgetAction?.('new', 'create')}
              className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Widget
            </button>
            
            {hybridMode && (
              <button
                onClick={() => onWidgetAction?.('chat', 'open')}
                className="flex items-center gap-2 px-4 py-2 border border-synrgy-primary/20 text-synrgy-primary rounded-lg hover:bg-synrgy-primary/10 transition-colors"
              >
                Start Conversation
              </button>
            )}
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className={`h-full overflow-auto ${className}`}>
      {/* Dashboard Header */}
      <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10">
        <div className="flex items-center gap-3">
          <LayoutDashboard className="w-5 h-5 text-synrgy-primary" />
          <div>
            <h2 className="text-lg font-semibold text-synrgy-text">Dashboard</h2>
            <div className="text-sm text-synrgy-muted">
              {pinnedWidgets.length} widget{pinnedWidgets.length !== 1 ? 's' : ''} pinned
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={optimizeLayout}
            className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
            title="Optimize layout"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => onWidgetAction?.('dashboard', 'settings')}
            className="p-2 rounded-lg text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
            title="Dashboard settings"
          >
            <Settings className="w-4 h-4" />
          </button>
          
          {pinnedWidgets.length > 0 && (
            <button
              onClick={clearAllWidgets}
              className="p-2 rounded-lg text-synrgy-muted hover:text-red-400 hover:bg-red-500/10 transition-colors"
              title="Clear all widgets"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Widget Grid */}
      <div className="p-6">
        <div className={`grid ${getGridLayout()} gap-6`}>
          <AnimatePresence mode="popLayout">
            {pinnedWidgets.map((widget) => (
              <motion.div
                key={widget.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ 
                  opacity: 1, 
                  scale: 1,
                  zIndex: expandedWidget === widget.id ? 50 : 1
                }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ 
                  type: "spring", 
                  damping: 25, 
                  stiffness: 300,
                  opacity: { duration: 0.2 }
                }}
                className={`relative ${
                  expandedWidget === widget.id 
                    ? 'fixed inset-4 z-50 bg-synrgy-bg-900/95 p-4 rounded-xl' 
                    : ''
                }`}
              >
                {renderWidget(widget)}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Expanded Widget Backdrop */}
      {expandedWidget && (
        <div
          className="fixed inset-0 bg-synrgy-bg-900/90 z-40"
          onClick={() => setExpandedWidget(null)}
        />
      )}
    </div>
  )
}
