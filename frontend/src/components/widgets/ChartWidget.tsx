import React from 'react'
import { BarChart3, TrendingUp, PieChart } from 'lucide-react'

import BaseWidget, { BaseWidgetProps } from './BaseWidget'
import VisualRenderer from '../Chat/VisualRenderer'
import type { DashboardWidget, VisualPayload } from '../../types'

interface ChartWidgetProps extends Omit<BaseWidgetProps, 'children'> {
  widget: DashboardWidget & { data: VisualPayload }
}

export default function ChartWidget(props: ChartWidgetProps) {
  const { widget, ...baseProps } = props
  
  // Determine chart icon based on chart type
  const getChartIcon = () => {
    if (widget.data?.type === 'composite' && widget.data.cards) {
      const chartCard = widget.data.cards.find(card => card.type === 'chart')
      if (chartCard?.chart_type === 'pie') return <PieChart className="w-4 h-4" />
      if (chartCard?.chart_type === 'line' || chartCard?.chart_type === 'timeseries') return <TrendingUp className="w-4 h-4" />
      return <BarChart3 className="w-4 h-4" />
    }
    return <BarChart3 className="w-4 h-4" />
  }

  // Custom refresh handler for chart data
  const handleRefresh = async () => {
    try {
      // Simulate data refresh - in real app, this would call an API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Update widget with new timestamp
      const updatedWidget = {
        ...widget,
        last_updated: new Date().toISOString()
      }
      
      // In real implementation, this would update the store
      console.log('Chart refreshed:', updatedWidget)
      
      // Call original refresh if provided
      baseProps.onRefresh?.()
    } catch (error) {
      console.error('Failed to refresh chart:', error)
    }
  }

  // Generate contextual Ask SYNRGY queries
  const generateContextualQueries = () => {
    const queries = [`Analyze the trends in ${widget.title}`]
    
    if (widget.data?.type === 'composite' && widget.data.cards) {
      widget.data.cards.forEach(card => {
        if (card.type === 'chart') {
          switch (card.chart_type) {
            case 'timeseries':
            case 'line':
              queries.push(`What patterns do you see in the time series data?`)
              queries.push(`Predict future trends based on this data`)
              break
            case 'bar':
              queries.push(`Which categories are performing best?`)
              queries.push(`Compare the values across different categories`)
              break
            case 'pie':
              queries.push(`What's the distribution breakdown?`)
              queries.push(`Which segments are most significant?`)
              break
          }
        }
      })
    }
    
    queries.push(`Generate a summary report for this chart data`)
    queries.push(`What anomalies or outliers do you detect?`)
    
    return queries
  }

  const handleAskSynrgy = (query: string) => {
    // Add chart context to the query
    const enrichedQuery = `Regarding the chart "${widget.title}": ${query}`
    baseProps.onAskSynrgy?.(enrichedQuery)
  }

  return (
    <BaseWidget
      {...baseProps}
      widget={widget}
      onRefresh={handleRefresh}
      onAskSynrgy={handleAskSynrgy}
    >
      <div className="relative">
        {/* Chart Header Info */}
        <div className="flex items-center gap-2 p-4 bg-synrgy-surface/30">
          <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
            {getChartIcon()}
          </div>
          <div className="flex-1">
            <div className="text-sm text-synrgy-muted">Data Visualization</div>
            {widget.data?.type === 'composite' && widget.data.cards && (
              <div className="text-xs text-synrgy-accent">
                {widget.data.cards.length} components
              </div>
            )}
          </div>
        </div>
        
        {/* Chart Content */}
        <div className="p-4">
          {widget.data ? (
            <VisualRenderer 
              payload={widget.data}
              className="widget-chart-container"
            />
          ) : (
            <div className="h-64 flex items-center justify-center text-synrgy-muted">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <div className="text-sm">No chart data available</div>
              </div>
            </div>
          )}
        </div>
        
        {/* Chart Metadata */}
        {widget.data?.type === 'composite' && widget.data.cards && (
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between text-xs text-synrgy-muted">
              <span>
                {widget.data.cards.filter(c => c.type === 'chart').length} charts
              </span>
              <span>
                {widget.data.cards.filter(c => c.type === 'summary_card').length} metrics
              </span>
              {widget.last_updated && (
                <span>
                  Updated {new Date(widget.last_updated).toLocaleString()}
                </span>
              )}
            </div>
          </div>
        )}
        
        {/* Quick Actions Bar */}
        <div className="border-t border-synrgy-primary/10 px-4 py-2">
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => handleAskSynrgy(`What are the key insights from this chart?`)}
              className="text-synrgy-accent hover:text-synrgy-primary transition-colors"
            >
              Get Insights
            </button>
            <span className="text-synrgy-muted">•</span>
            <button
              onClick={() => handleAskSynrgy(`Generate a detailed report for this data`)}
              className="text-synrgy-accent hover:text-synrgy-primary transition-colors"
            >
              Generate Report
            </button>
            <span className="text-synrgy-muted">•</span>
            <button
              onClick={() => handleAskSynrgy(`Check for anomalies in this data`)}
              className="text-synrgy-accent hover:text-synrgy-primary transition-colors"
            >
              Find Anomalies
            </button>
          </div>
        </div>
      </div>
    </BaseWidget>
  )
}
