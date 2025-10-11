import React from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield, Activity } from 'lucide-react'

import BaseWidget, { BaseWidgetProps } from './BaseWidget'
import type { DashboardWidget, SummaryCard } from '../../types'

interface SummaryCardWidgetProps extends Omit<BaseWidgetProps, 'children'> {
  widget: DashboardWidget & { data: SummaryCard }
}

export default function SummaryCardWidget(props: SummaryCardWidgetProps) {
  const { widget, ...baseProps } = props
  const { data } = widget

  // Get appropriate icon based on widget type or title
  const getMetricIcon = () => {
    const title = widget.title.toLowerCase()
    
    if (title.includes('threat') || title.includes('alert') || title.includes('critical')) {
      return <AlertTriangle className="w-5 h-5" />
    }
    if (title.includes('security') || title.includes('blocked') || title.includes('protected')) {
      return <Shield className="w-5 h-5" />
    }
    return <Activity className="w-5 h-5" />
  }

  // Get trend icon and color
  const getTrendIndicator = () => {
    if (!data.change) return null

    const { trend, value } = data.change
    const isPositive = value > 0
    const isNegative = value < 0

    let icon, colorClass
    switch (trend) {
      case 'up':
        icon = <TrendingUp className="w-3 h-3" />
        colorClass = isPositive ? 'text-green-500' : 'text-red-500'
        break
      case 'down':
        icon = <TrendingDown className="w-3 h-3" />
        colorClass = isNegative ? 'text-green-500' : 'text-red-500'
        break
      case 'stable':
      default:
        icon = <Minus className="w-3 h-3" />
        colorClass = 'text-synrgy-muted'
        break
    }

    return (
      <div className={`flex items-center gap-1 ${colorClass}`}>
        {icon}
        <span className="text-xs">
          {Math.abs(value).toFixed(1)}%
        </span>
      </div>
    )
  }

  // Get status color
  const getStatusColor = () => {
    switch (data.status) {
      case 'critical':
        return 'border-red-500/50 bg-red-500/5'
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/5'
      case 'normal':
      default:
        return 'border-synrgy-primary/20 bg-synrgy-surface/30'
    }
  }

  // Get value color based on status
  const getValueColor = () => {
    switch (data.status) {
      case 'critical':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      case 'normal':
      default:
        return 'text-synrgy-text'
    }
  }

  // Format the main value
  const formatValue = (value: string | number) => {
    if (typeof value === 'number') {
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`
      } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K`
      }
      return value.toLocaleString()
    }
    return value
  }

  const handleAskSynrgy = (query: string) => {
    // Add metric context to the query
    const enrichedQuery = `Regarding the metric "${widget.title}" (current value: ${data.value}): ${query}`
    baseProps.onAskSynrgy?.(enrichedQuery)
  }

  return (
    <BaseWidget
      {...baseProps}
      widget={widget}
      onAskSynrgy={handleAskSynrgy}
      className={`border-2 ${getStatusColor()}`}
    >
      <div className="p-6">
        {/* Header with Icon and Status */}
        <div className="flex items-start justify-between mb-4">
          <div className={`w-10 h-10 rounded-lg bg-synrgy-primary/10 flex items-center justify-center text-synrgy-primary`}>
            {getMetricIcon()}
          </div>
          
          {data.status && data.status !== 'normal' && (
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${
              data.status === 'critical' 
                ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
            }`}>
              {data.status.toUpperCase()}
            </div>
          )}
        </div>

        {/* Main Value */}
        <div className="mb-2">
          <div className={`text-3xl font-bold ${getValueColor()}`}>
            {formatValue(data.value)}
          </div>
          <div className="text-sm text-synrgy-muted mt-1">
            {data.title || widget.title}
          </div>
        </div>

        {/* Trend Information */}
        {data.change && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getTrendIndicator()}
              <span className="text-xs text-synrgy-muted">
                vs {data.change.period || 'previous period'}
              </span>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-4 pt-4 border-t border-synrgy-primary/10">
          <div className="flex items-center gap-3 text-xs">
            <button
              onClick={() => handleAskSynrgy(`Why is this metric at ${data.value}?`)}
              className="text-synrgy-accent hover:text-synrgy-primary transition-colors"
            >
              Explain Value
            </button>
            <span className="text-synrgy-muted">•</span>
            <button
              onClick={() => handleAskSynrgy(`What caused the recent changes in this metric?`)}
              className="text-synrgy-accent hover:text-synrgy-primary transition-colors"
            >
              Analyze Trends
            </button>
            {data.status === 'critical' && (
              <>
                <span className="text-synrgy-muted">•</span>
                <button
                  onClick={() => handleAskSynrgy(`What actions should I take for this critical metric?`)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  Get Actions
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </BaseWidget>
  )
}
