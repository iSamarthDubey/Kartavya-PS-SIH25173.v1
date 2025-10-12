/**
 * SYNRGY SummaryCardRenderer
 * Displays key security metrics and indicators
 * Based on SYNRGY.TXT summary card specifications
 */

import React from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield, Activity, Users } from 'lucide-react'
import type { VisualCard, SummaryCard } from '@/types'

interface SummaryCardRendererProps {
  card: VisualCard
  compact?: boolean
  onError?: (error: any) => void
}

/**
 * Icon mapping for different card types
 */
const CARD_ICONS = {
  alerts: AlertTriangle,
  security: Shield,
  activity: Activity,
  users: Users,
  default: Activity
}

/**
 * Color mapping for status and trends
 */
const STATUS_COLORS = {
  success: 'text-green-400 bg-green-400/10 border-green-400/20',
  warning: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  error: 'text-red-400 bg-red-400/10 border-red-400/20',
  info: 'text-synrgy-primary bg-synrgy-primary/10 border-synrgy-primary/20',
  critical: 'text-red-500 bg-red-500/20 border-red-500/30'
}

const TREND_COLORS = {
  up: 'text-green-400',
  down: 'text-red-400',
  stable: 'text-synrgy-muted'
}

/**
 * Format large numbers with appropriate units
 */
const formatValue = (value: number | string): string => {
  if (typeof value === 'string') return value
  
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  return value.toString()
}

/**
 * Get trend icon based on direction
 */
const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
  switch (trend) {
    case 'up': return TrendingUp
    case 'down': return TrendingDown
    case 'stable': return Minus
    default: return Minus
  }
}

/**
 * Mini sparkline chart for trends
 */
const MiniSparkline: React.FC<{ data: Array<{ x: string, y: number }> }> = ({ data }) => {
  if (!data || data.length === 0) return null
  
  const maxY = Math.max(...data.map(d => d.y))
  const minY = Math.min(...data.map(d => d.y))
  const range = maxY - minY || 1
  
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - ((point.y - minY) / range) * 100
    return `${x},${y}`
  }).join(' ')
  
  return (
    <div className="w-16 h-6">
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        preserveAspectRatio="none"
      >
        <polyline
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          points={points}
          className="text-synrgy-primary opacity-60"
        />
      </svg>
    </div>
  )
}

/**
 * Main SummaryCardRenderer component
 */
const SummaryCardRenderer: React.FC<SummaryCardRendererProps> = ({
  card,
  compact = false,
  onError
}) => {
  try {
    const summaryCard = card as SummaryCard
    
    // Get icon component
    const iconKey = summaryCard.icon || 'default'
    const IconComponent = CARD_ICONS[iconKey as keyof typeof CARD_ICONS] || CARD_ICONS.default
    
    // Get status colors
    const statusClass = STATUS_COLORS[summaryCard.status || 'info']
    
    // Get trend colors and icon
    const trendColor = summaryCard.trend ? TREND_COLORS[summaryCard.trend] : ''
    const TrendIcon = summaryCard.trend ? getTrendIcon(summaryCard.trend) : null
    
    // Format the main value
    const formattedValue = formatValue(summaryCard.value)
    
    return (
      <div className={`
        p-4 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10
        hover:border-synrgy-primary/30 transition-all duration-200
        ${compact ? 'p-3' : 'p-4'}
      `}>
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${statusClass}`}>
              <IconComponent className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className={`font-medium text-synrgy-text truncate ${compact ? 'text-sm' : 'text-base'}`}>
                {summaryCard.title}
              </h3>
              {summaryCard.subtitle && !compact && (
                <p className="text-xs text-synrgy-muted mt-0.5 truncate">
                  {summaryCard.subtitle}
                </p>
              )}
            </div>
          </div>
          
          {/* Sparkline */}
          {summaryCard.sparkline && !compact && (
            <MiniSparkline data={summaryCard.sparkline} />
          )}
        </div>
        
        {/* Main Value */}
        <div className="flex items-baseline gap-2 mb-2">
          <span className={`font-bold ${compact ? 'text-xl' : 'text-2xl'} text-synrgy-text`}>
            {formattedValue}
          </span>
          {summaryCard.unit && (
            <span className="text-sm text-synrgy-muted">
              {summaryCard.unit}
            </span>
          )}
        </div>
        
        {/* Comparison & Trend */}
        {summaryCard.comparison && !compact && (
          <div className="flex items-center gap-2 text-xs">
            {TrendIcon && (
              <TrendIcon className={`w-3 h-3 ${trendColor}`} />
            )}
            <span className={trendColor}>
              {summaryCard.comparison.change > 0 ? '+' : ''}
              {summaryCard.comparison.change}%
            </span>
            <span className="text-synrgy-muted">
              vs {summaryCard.comparison.period}
            </span>
          </div>
        )}
        
        {/* Status Indicator (compact mode) */}
        {compact && summaryCard.status && (
          <div className="flex items-center gap-1 mt-2">
            <div className={`w-2 h-2 rounded-full ${statusClass.split(' ')[1]}`} />
            <span className="text-xs text-synrgy-muted capitalize">
              {summaryCard.status}
            </span>
          </div>
        )}
      </div>
    )
  } catch (error) {
    onError?.(error)
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-red-400 text-sm">
          Failed to render summary card: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }
}

export default SummaryCardRenderer
