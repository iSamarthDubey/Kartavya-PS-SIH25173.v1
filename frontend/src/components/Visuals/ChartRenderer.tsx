/**
 * SYNRGY ChartRenderer
 * Interactive security charts using Recharts
 * Supports timeseries, bar, pie, scatter, heatmap charts
 */

import React, { useState, useMemo } from 'react'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  PieChart, Pie, Cell, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from 'recharts'
import { Calendar, TrendingUp, BarChart3, PieChart as PieChartIcon } from 'lucide-react'
import type { VisualCard, ChartCard } from '@/types'

interface ChartRendererProps {
  card: VisualCard
  compact?: boolean
  onError?: (error: any) => void
}

/**
 * SYNRGY chart colors based on design tokens
 */
const CHART_COLORS = {
  primary: '#00EFFF',    // Electric cyan
  accent: '#FF7A00',     // Solar orange  
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  muted: '#94A3B8',
  gradient: ['#00EFFF', '#FF7A00', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
}

/**
 * Format timestamp for display
 */
const formatTimestamp = (timestamp: string | number) => {
  const date = new Date(timestamp)
  
  // For recent data (last 24h), show time only
  const now = new Date()
  const timeDiff = now.getTime() - date.getTime()
  const hoursDiff = timeDiff / (1000 * 3600)
  
  if (hoursDiff < 24) {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
  
  // For older data, show date
  if (hoursDiff < 24 * 7) {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: '2-digit' 
  })
}

/**
 * Format value for display
 */
const formatValue = (value: number) => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
  return value.toString()
}

/**
 * Custom tooltip for all chart types
 */
const CustomTooltip = ({ active, payload, label, chart_type }: any) => {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div className="bg-synrgy-surface/95 backdrop-blur-sm border border-synrgy-primary/20 rounded-lg p-3 shadow-lg">
      <p className="text-synrgy-text font-medium mb-2">
        {chart_type === 'timeseries' ? formatTimestamp(label) : label}
      </p>
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-2">
          <div 
            className="w-2 h-2 rounded-full" 
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-synrgy-muted text-sm">
            {entry.name}: 
          </span>
          <span className="text-synrgy-text font-medium">
            {formatValue(entry.value)}
          </span>
        </div>
      ))}
    </div>
  )
}

/**
 * Timeseries Chart Component
 */
const TimeseriesChart: React.FC<{ 
  data: any[], 
  chartCard: ChartCard, 
  compact: boolean 
}> = ({ data, chartCard, compact }) => {
  const [chartType, setChartType] = useState<'line' | 'area'>('line')

  return (
    <>
      {/* Chart Type Toggle */}
      {!compact && (
        <div className="flex items-center gap-2 mb-2">
          <button
            onClick={() => setChartType('line')}
            className={`p-1 rounded ${chartType === 'line' ? 'bg-synrgy-primary/20 text-synrgy-primary' : 'text-synrgy-muted hover:text-synrgy-text'}`}
          >
            <TrendingUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => setChartType('area')}
            className={`p-1 rounded ${chartType === 'area' ? 'bg-synrgy-primary/20 text-synrgy-primary' : 'text-synrgy-muted hover:text-synrgy-text'}`}
          >
            <BarChart3 className="w-4 h-4" />
          </button>
        </div>
      )}

      <ResponsiveContainer width="100%" height={compact ? 200 : 300}>
        {chartType === 'area' ? (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
            <XAxis 
              dataKey={chartCard.axes?.x?.label || 'timestamp'}
              tick={{ fontSize: 12, fill: '#94A3B8' }}
              tickFormatter={formatTimestamp}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#94A3B8' }}
              tickFormatter={formatValue}
            />
            <Tooltip content={<CustomTooltip chart_type="timeseries" />} />
            <Area
              type="monotone"
              dataKey={chartCard.axes?.y?.label || 'value'}
              stroke={CHART_COLORS.primary}
              fill={CHART_COLORS.primary}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </AreaChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
            <XAxis 
              dataKey={chartCard.axes?.x?.label || 'timestamp'}
              tick={{ fontSize: 12, fill: '#94A3B8' }}
              tickFormatter={formatTimestamp}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#94A3B8' }}
              tickFormatter={formatValue}
            />
            <Tooltip content={<CustomTooltip chart_type="timeseries" />} />
            <Line
              type="monotone"
              dataKey={chartCard.axes?.y?.label || 'value'}
              stroke={CHART_COLORS.primary}
              strokeWidth={2}
              dot={{ r: 3, fill: CHART_COLORS.primary }}
              activeDot={{ r: 5, fill: CHART_COLORS.accent }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </>
  )
}

/**
 * Bar Chart Component
 */
const BarChartComponent: React.FC<{ 
  data: any[], 
  chartCard: ChartCard, 
  compact: boolean 
}> = ({ data, chartCard, compact }) => (
  <ResponsiveContainer width="100%" height={compact ? 200 : 300}>
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
      <XAxis 
        dataKey={chartCard.axes?.x?.label || 'name'}
        tick={{ fontSize: 12, fill: '#94A3B8' }}
      />
      <YAxis 
        tick={{ fontSize: 12, fill: '#94A3B8' }}
        tickFormatter={formatValue}
      />
      <Tooltip content={<CustomTooltip chart_type="bar" />} />
      <Bar
        dataKey={chartCard.axes?.y?.label || 'value'}
        fill={CHART_COLORS.primary}
        radius={[2, 2, 0, 0]}
      />
    </BarChart>
  </ResponsiveContainer>
)

/**
 * Pie Chart Component  
 */
const PieChartComponent: React.FC<{ 
  data: any[], 
  chartCard: ChartCard, 
  compact: boolean 
}> = ({ data, chartCard, compact }) => (
  <ResponsiveContainer width="100%" height={compact ? 200 : 300}>
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        outerRadius={compact ? 60 : 80}
        dataKey={chartCard.axes?.y?.label || 'value'}
        nameKey={chartCard.axes?.x?.label || 'name'}
      >
        {data.map((entry, index) => (
          <Cell 
            key={`cell-${index}`} 
            fill={CHART_COLORS.gradient[index % CHART_COLORS.gradient.length]} 
          />
        ))}
      </Pie>
      <Tooltip content={<CustomTooltip chart_type="pie" />} />
      {!compact && <Legend />}
    </PieChart>
  </ResponsiveContainer>
)

/**
 * Main ChartRenderer component
 */
const ChartRenderer: React.FC<ChartRendererProps> = ({
  card,
  compact = false,
  onError
}) => {
  try {
    const chartCard = card as ChartCard
    
    // Validate data
    if (!chartCard.data || !Array.isArray(chartCard.data) || chartCard.data.length === 0) {
      return (
        <div className="p-6 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10 text-center">
          <BarChart3 className="w-8 h-8 text-synrgy-muted mx-auto mb-2" />
          <p className="text-synrgy-muted text-sm">No chart data available</p>
        </div>
      )
    }

    const chartHeight = compact ? 200 : 300

    return (
      <div className="bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10 p-4">
        {/* Chart Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className={`font-medium text-synrgy-text ${compact ? 'text-sm' : 'text-base'}`}>
              {chartCard.title || 'Security Chart'}
            </h3>
            {chartCard.subtitle && !compact && (
              <p className="text-xs text-synrgy-muted mt-0.5">
                {chartCard.subtitle}
              </p>
            )}
          </div>
          
          {/* Chart Type Icon */}
          <div className="text-synrgy-primary">
            {chartCard.chart_type === 'pie' && <PieChartIcon className="w-5 h-5" />}
            {chartCard.chart_type === 'bar' && <BarChart3 className="w-5 h-5" />}
            {(chartCard.chart_type === 'timeseries' || chartCard.chart_type === 'line') && <TrendingUp className="w-5 h-5" />}
            {!chartCard.chart_type && <BarChart3 className="w-5 h-5" />}
          </div>
        </div>

        {/* Chart Content */}
        <div style={{ height: chartHeight }}>
          {(chartCard.chart_type === 'timeseries' || chartCard.chart_type === 'line' || chartCard.chart_type === 'area') && (
            <TimeseriesChart 
              data={chartCard.data} 
              chartCard={chartCard} 
              compact={compact} 
            />
          )}
          
          {chartCard.chart_type === 'bar' && (
            <BarChartComponent 
              data={chartCard.data} 
              chartCard={chartCard} 
              compact={compact} 
            />
          )}
          
          {chartCard.chart_type === 'pie' && (
            <PieChartComponent 
              data={chartCard.data} 
              chartCard={chartCard} 
              compact={compact} 
            />
          )}
          
          {/* Default to bar chart if type not specified */}
          {!chartCard.chart_type && (
            <BarChartComponent 
              data={chartCard.data} 
              chartCard={chartCard} 
              compact={compact} 
            />
          )}
        </div>
        
        {/* Chart Footer Stats */}
        {!compact && chartCard.data && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-synrgy-primary/10">
            <div className="flex items-center gap-4 text-xs text-synrgy-muted">
              <span>
                Data points: {chartCard.data.length}
              </span>
              {chartCard.metadata?.execution_time && (
                <span>
                  Query time: {chartCard.metadata.execution_time}ms
                </span>
              )}
            </div>
            <Calendar className="w-4 h-4 text-synrgy-muted" />
          </div>
        )}
      </div>
    )
  } catch (error) {
    onError?.(error)
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-red-400 text-sm">
          Failed to render chart: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }
}

export default ChartRenderer
