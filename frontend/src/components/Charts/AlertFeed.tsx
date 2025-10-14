/**
 * SYNRGY Alert Feed Component
 * Displays real-time scrolling security alerts with severity indicators
 */

import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  AlertTriangle, 
  Shield, 
  Bug, 
  Zap, 
  Eye, 
  Clock,
  ChevronRight,
  Pause,
  Play
} from 'lucide-react'

interface SecurityAlert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  timestamp: string
  category: string
  source?: string
  ip?: string
  user?: string
}

interface AlertFeedProps {
  alerts: SecurityAlert[]
  maxVisible?: number
  autoScroll?: boolean
  showTimestamps?: boolean
  compact?: boolean
  className?: string
}

const SEVERITY_CONFIG = {
  critical: {
    icon: AlertTriangle,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    pulse: 'animate-pulse'
  },
  high: {
    icon: Shield,
    color: 'text-orange-400', 
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
    pulse: ''
  },
  medium: {
    icon: Bug,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10', 
    border: 'border-yellow-500/20',
    pulse: ''
  },
  low: {
    icon: Eye,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20', 
    pulse: ''
  },
  info: {
    icon: Zap,
    color: 'text-synrgy-primary',
    bg: 'bg-synrgy-primary/10',
    border: 'border-synrgy-primary/20',
    pulse: ''
  }
}

export default function AlertFeed({
  alerts,
  maxVisible = 10,
  autoScroll = true,
  showTimestamps = true,
  compact = false,
  className = ''
}: AlertFeedProps) {
  const [isPaused, setIsPaused] = useState(false)
  const [visibleAlerts, setVisibleAlerts] = useState<SecurityAlert[]>([])

  // Update visible alerts based on auto-scroll and pause state
  useEffect(() => {
    if (!autoScroll || isPaused) return

    const sortedAlerts = [...alerts]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, maxVisible)

    setVisibleAlerts(sortedAlerts)
  }, [alerts, maxVisible, autoScroll, isPaused])

  // Initialize visible alerts
  useEffect(() => {
    const initial = [...alerts]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, maxVisible)
    
    setVisibleAlerts(initial)
  }, [])

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  const AlertItem = ({ alert, index }: { alert: SecurityAlert; index: number }) => {
    const config = SEVERITY_CONFIG[alert.severity]
    const Icon = config.icon

    return (
      <motion.div
        key={alert.id}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        transition={{ duration: 0.3, delay: index * 0.05 }}
        className={`
          relative group p-3 border rounded-lg transition-all duration-200
          hover:scale-[1.01] cursor-pointer
          ${config.bg} ${config.border} ${config.pulse}
          ${compact ? 'p-2' : 'p-3'}
        `}
      >
        {/* Severity indicator */}
        <div className="flex items-start gap-3">
          <div className={`flex-shrink-0 ${config.color} mt-0.5`}>
            <Icon className={compact ? 'w-4 h-4' : 'w-5 h-5'} />
          </div>
          
          <div className="flex-1 min-w-0">
            {/* Alert title and category */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <h4 className={`font-medium text-synrgy-text line-clamp-1 ${compact ? 'text-sm' : ''}`}>
                  {alert.title}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-2 py-0.5 rounded ${config.color} ${config.bg}`}>
                    {alert.category}
                  </span>
                  <span className={`text-xs text-synrgy-muted uppercase ${config.color}`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
              
              {showTimestamps && (
                <div className="flex items-center gap-1 text-xs text-synrgy-muted flex-shrink-0">
                  <Clock className="w-3 h-3" />
                  <span>{formatTimestamp(alert.timestamp)}</span>
                </div>
              )}
            </div>

            {/* Alert description */}
            {!compact && (
              <p className="text-sm text-synrgy-muted mt-2 line-clamp-2">
                {alert.description}
              </p>
            )}

            {/* Additional metadata */}
            <div className="flex items-center gap-4 mt-2 text-xs text-synrgy-muted">
              {alert.source && (
                <span>Source: <span className="text-synrgy-text">{alert.source}</span></span>
              )}
              {alert.ip && (
                <span>IP: <span className="text-synrgy-text font-mono">{alert.ip}</span></span>
              )}
              {alert.user && (
                <span>User: <span className="text-synrgy-text">{alert.user}</span></span>
              )}
            </div>
          </div>

          {/* Action arrow */}
          <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <ChevronRight className="w-4 h-4 text-synrgy-muted" />
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-synrgy-text">
          Security Alerts
          <span className="ml-2 text-sm text-synrgy-muted">
            ({alerts.length} total)
          </span>
        </h3>
        
        {autoScroll && (
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`
              flex items-center gap-2 px-3 py-1 rounded text-sm transition-colors
              ${isPaused 
                ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
              }
            `}
          >
            {isPaused ? (
              <>
                <Play className="w-4 h-4" />
                Resume
              </>
            ) : (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            )}
          </button>
        )}
      </div>

      {/* Alert feed */}
      <div className={`space-y-2 ${compact ? 'space-y-1' : 'space-y-2'}`}>
        {visibleAlerts.length > 0 ? (
          <AnimatePresence mode="popLayout">
            {visibleAlerts.map((alert, index) => (
              <AlertItem key={alert.id} alert={alert} index={index} />
            ))}
          </AnimatePresence>
        ) : (
          <div className="text-center py-8 text-synrgy-muted">
            <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No security alerts at this time</p>
          </div>
        )}
      </div>

      {/* Footer with stats */}
      {alerts.length > maxVisible && (
        <div className="text-xs text-synrgy-muted text-center pt-2 border-t border-synrgy-primary/10">
          Showing {Math.min(visibleAlerts.length, maxVisible)} of {alerts.length} alerts
        </div>
      )}
    </div>
  )
}
