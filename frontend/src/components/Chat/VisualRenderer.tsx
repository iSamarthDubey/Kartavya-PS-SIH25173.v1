/**
 * SYNRGY Chat VisualRenderer - Enhanced visualization component
 * Handles all chart types, tables, and visual data rendering
 */

import { useState, useCallback, useMemo, Suspense } from 'react'
import { motion } from 'framer-motion'
import {
  Pin,
  Info,
  TrendingUp,
  BarChart3,
  PieChart,
  Maximize2,
  Download,
  MapPin,
  Globe,
  Table,
  Filter as FilterIcon,
  Loader2,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'

import { useVisualPerformance } from '@/hooks/useVisualPerformance'
import type { VisualPayload, VisualCard } from '@/types'

interface VisualRendererProps {
  payload: VisualPayload
  className?: string
  onPin?: (card: VisualCard) => void
  onExport?: (card: VisualCard) => void
  interactive?: boolean
  compact?: boolean
}

// SYNRGY color palette for charts
const CHART_COLORS = [
  '#00EFFF', // synrgy-primary
  '#FF7A00', // synrgy-accent
  '#22D3EE', // cyan-400
  '#F97316', // orange-500
  '#06B6D4', // cyan-500
  '#EA580C', // orange-600
  '#0891B2', // cyan-600
  '#C2410C', // orange-700
]


export default function VisualRenderer({
  payload,
  className = '',
  onPin,
  onExport,
  interactive = true,
  compact = false,
}: VisualRendererProps) {
  const [expandedCard, setExpandedCard] = useState<string | null>(null)
  
  // Performance optimization hook
  const {
    optimizePayload,
    shouldLazyLoad,
    getMetrics,
  } = useVisualPerformance({
    cacheEnabled: true,
    performanceTracking: import.meta.env.DEV,
  })

  if (!payload) return null

  // Optimize payload for performance
  const optimizedPayload = useMemo(() => optimizePayload(payload), [payload, optimizePayload])

  // Handle composite payload with multiple cards
  const cards = optimizedPayload.cards || [optimizedPayload as VisualCard]
  const isComposite = optimizedPayload.type === 'composite' && optimizedPayload.cards && optimizedPayload.cards.length > 0

  const handlePin = useCallback(
    (card: VisualCard) => {
      if (onPin && interactive) {
        onPin(card)
      }
    },
    [onPin, interactive]
  )


  const renderSummaryCard = (card: VisualCard, index: number) => (
    <motion.div
      key={`summary-${index}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="bg-synrgy-surface/50 border border-synrgy-primary/20 rounded-xl p-6 hover:border-synrgy-primary/40 transition-all duration-200"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-synrgy-primary rounded-full" />
          <h3 className="text-sm font-medium text-synrgy-muted">{card.title}</h3>
        </div>
        <button className="opacity-50 hover:opacity-100 transition-opacity">
          <Pin className="w-4 h-4 text-synrgy-muted" />
        </button>
      </div>

      <div className="text-3xl font-bold text-synrgy-text mb-1">
        {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
      </div>

      {/* Optional trend indicator */}
      {card.trend && (
        <div className="flex items-center gap-1 text-xs mt-2">
          <TrendingUp
            className={`w-3 h-3 ${
              card.trend === 'up'
                ? 'text-green-500'
                : card.trend === 'down'
                  ? 'text-red-500'
                  : 'text-synrgy-muted'
            }`}
          />
          <span className="text-synrgy-muted">vs last period</span>
        </div>
      )}

      {/* Action buttons */}
      {interactive && (
        <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2 flex gap-1">
          <button
            onClick={() => handlePin(card)}
            className="p-1 bg-synrgy-primary/20 hover:bg-synrgy-primary/30 rounded text-synrgy-primary"
            title="Pin to Dashboard"
          >
            <Pin className="w-3 h-3" />
          </button>
        </div>
      )}
    </motion.div>
  )

  const renderChart = (card: VisualCard, index: number) => {
    if (!card.data || !Array.isArray(card.data)) return null

    const isExpanded = expandedCard === `chart-${index}`

    // Dynamic field mapping from config
    const config = card.config || {}
    const xField = config.x_field || 'x'
    const yField = config.y_field || 'y'
    // Dynamic field mapping configuration available for future use

    // Process data with dynamic field mapping
    const processedData = card.data.map((item: any) => ({
      ...item,
      x: item[xField] || item.x,
      y: item[yField] || item.y,
      name: item.name || item[xField] || item.x,
      value: item.value || item[yField] || item.y,
    }))

    let chartBody: JSX.Element | null = null

    if (card.chart_type === 'bar') {
      chartBody = (
        <BarChart data={processedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
          <XAxis dataKey="x" stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
          <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F1724',
              border: '1px solid #00EFFF',
              borderRadius: '8px',
              color: '#E6EEF8',
            }}
          />
          <Bar dataKey="y" fill={config.color || '#00EFFF'} radius={[4, 4, 0, 0]} />
        </BarChart>
      )
    }

    if (card.chart_type === 'line' || card.chart_type === 'timeseries') {
      chartBody = (
        <LineChart data={processedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
          <XAxis
            dataKey="x"
            stroke="#94A3B8"
            fontSize={12}
            tick={{ fill: '#94A3B8' }}
            type={card.chart_type === 'timeseries' ? 'category' : 'category'}
          />
          <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F1724',
              border: '1px solid #00EFFF',
              borderRadius: '8px',
              color: '#E6EEF8',
            }}
          />
          <Line
            type="monotone"
            dataKey="y"
            stroke={config.color || '#00EFFF'}
            strokeWidth={config.strokeWidth || 3}
            dot={{ fill: config.color || '#00EFFF', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, fill: '#FF7A00' }}
          />
        </LineChart>
      )
    }

    if (card.chart_type === 'area') {
      const gradientId = `gradient-${index}`
      chartBody = (
        <AreaChart data={processedData}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={config.color || '#00EFFF'} stopOpacity={0.8} />
              <stop offset="95%" stopColor={config.color || '#00EFFF'} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
          <XAxis dataKey="x" stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
          <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F1724',
              border: '1px solid #00EFFF',
              borderRadius: '8px',
              color: '#E6EEF8',
            }}
          />
          <Area
            type="monotone"
            dataKey="y"
            stroke={config.color || '#00EFFF'}
            strokeWidth={config.strokeWidth || 2}
            fillOpacity={1}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      )
    }

    if (card.chart_type === 'pie') {
      chartBody = (
        <RechartsPieChart>
          <Pie
            data={processedData}
            cx="50%"
            cy="50%"
            outerRadius={config.outerRadius || 80}
            fill={config.color || '#00EFFF'}
            dataKey="value"
            label={({ name, percent }: { name: string; percent: number }) =>
              `${name}: ${(percent * 100).toFixed(1)}%`
            }
          >
            {processedData.map((_, dataIndex) => (
              <Cell
                key={`cell-${dataIndex}`}
                fill={CHART_COLORS[dataIndex % CHART_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F1724',
              border: '1px solid #00EFFF',
              borderRadius: '8px',
              color: '#E6EEF8',
            }}
          />
        </RechartsPieChart>
      )
    }

    if (!chartBody) {
      return null
    }

    return (
      <motion.div
        key={`chart-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className={`bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6 ${
          isExpanded ? 'col-span-2' : ''
        }`}
      >
        {/* Chart Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
              {card.chart_type === 'bar' && <BarChart3 className="w-4 h-4 text-synrgy-primary" />}
              {(card.chart_type === 'line' || card.chart_type === 'timeseries') && (
                <TrendingUp className="w-4 h-4 text-synrgy-primary" />
              )}
              {card.chart_type === 'pie' && <PieChart className="w-4 h-4 text-synrgy-primary" />}
              {card.chart_type === 'area' && <TrendingUp className="w-4 h-4 text-synrgy-primary" />}
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">{card.title}</h3>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setExpandedCard(isExpanded ? null : `chart-${index}`)}
              className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              title={isExpanded ? 'Minimize' : 'Expand'}
            >
              <Maximize2 className="w-4 h-4 text-synrgy-muted" />
            </button>
            <button
              className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              title="Export chart"
            >
              <Download className="w-4 h-4 text-synrgy-muted" />
            </button>
          </div>
        </div>

        {/* Chart Content */}
        <div className={`${isExpanded ? 'h-96' : 'h-64'}`}>
          <ResponsiveContainer width="100%" height="100%">
            {chartBody}
          </ResponsiveContainer>
        </div>
      </motion.div>
    )
  }

  const renderMap = (card: VisualCard, index: number) => {
    if (!card.data) return null

    return (
      <motion.div
        key={`map-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
              <MapPin className="w-4 h-4 text-synrgy-primary" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">{card.title}</h3>
          </div>
        </div>

        {/* Data-driven map content */}
        <div className="space-y-3">
          {Array.isArray(card.data) ? (
            card.data.slice(0, 10).map((location: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-synrgy-surface/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-synrgy-primary rounded-full" />
                  <div>
                    <div className="text-sm font-medium text-synrgy-text">
                      {location.name || location.location || location.ip || 'Location'}
                    </div>
                    {location.coordinates && (
                      <div className="text-xs text-synrgy-muted">
                        {location.coordinates.lat}, {location.coordinates.lng}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-sm text-synrgy-accent">
                  {location.count || location.value || location.events || 0}
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-synrgy-muted">No location data available</div>
          )}
        </div>
      </motion.div>
    )
  }

  const renderNetworkGraph = (card: VisualCard, index: number) => {
    if (!card.data) return null

    return (
      <motion.div
        key={`network-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
              <Globe className="w-4 h-4 text-synrgy-primary" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">{card.title}</h3>
          </div>
        </div>

        {/* Data-driven network content */}
        <div className="space-y-4">
          {card.data && typeof card.data === 'object' && (card.data as any).nodes && (
            <div>
              <div className="text-sm font-medium text-synrgy-text mb-2">Network Nodes</div>
              <div className="grid grid-cols-2 gap-2">
                {((card.data as any).nodes as any[]).slice(0, 8).map((node: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-2 bg-synrgy-surface/50 rounded"
                  >
                    <div
                      className={`w-3 h-3 rounded-full ${node.type === 'source' ? 'bg-synrgy-primary' : 'bg-synrgy-accent'}`}
                    />
                    <div className="text-xs text-synrgy-text truncate">
                      {node.id || node.name || node.ip}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {card.data && typeof card.data === 'object' && (card.data as any).edges && (
            <div>
              <div className="text-sm font-medium text-synrgy-text mb-2">Network Connections</div>
              <div className="space-y-1">
                {((card.data as any).edges as any[]).slice(0, 5).map((edge: any, idx: number) => (
                  <div key={idx} className="text-xs text-synrgy-muted flex items-center gap-2">
                    <span>{edge.source}</span>
                    <span>→</span>
                    <span>{edge.target}</span>
                    {edge.weight && <span className="text-synrgy-accent">({edge.weight})</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    )
  }

  const renderNarrative = (card: VisualCard, index: number) => {
    if (!card.data && !card.value) return null

    return (
      <motion.div
        key={`narrative-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6"
      >
        {card.title && (
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 bg-synrgy-primary rounded" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">{card.title}</h3>
          </div>
        )}

        <div className="prose prose-invert prose-sm max-w-none">
          <div className="text-synrgy-text leading-relaxed">
            {typeof card.value === 'string'
              ? card.value
              : typeof card.data === 'string'
                ? card.data
                : (card.data && typeof card.data === 'object'
                    ? (card.data as any).narrative || (card.data as any).content
                    : null) || 'No narrative content available'}
          </div>
        </div>
      </motion.div>
    )
  }

  const renderTable = (card: VisualCard, index: number) => {
    if (!card.columns || !card.rows) return null

    return (
      <motion.div
        key={`table-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl overflow-hidden"
      >
        {/* Table Header */}
        <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
              <Table className="w-4 h-4 text-synrgy-primary" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">{card.title}</h3>
          </div>

          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors">
              <FilterIcon className="w-4 h-4 text-synrgy-muted" />
            </button>
            <button className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors">
              <Download className="w-4 h-4 text-synrgy-muted" />
            </button>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-synrgy-surface/50">
              <tr>
                {card.columns.map((column, colIndex) => (
                  <th
                    key={colIndex}
                    className="px-6 py-4 text-left text-xs font-medium text-synrgy-muted uppercase tracking-wider border-b border-synrgy-primary/10"
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {card.rows.slice(0, 10).map((row, rowIndex) => (
                <motion.tr
                  key={rowIndex}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: rowIndex * 0.05 }}
                  className="hover:bg-synrgy-primary/5 transition-colors"
                >
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className="px-6 py-4 text-sm text-synrgy-text border-b border-synrgy-primary/5"
                    >
                      {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                    </td>
                  ))}
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination info */}
        {card.rows.length > 10 && (
          <div className="px-6 py-3 bg-synrgy-surface/30 border-t border-synrgy-primary/10">
            <div className="text-xs text-synrgy-muted">
              Showing 10 of {card.rows.length} results
            </div>
          </div>
        )}
      </motion.div>
    )
  }

  const renderCard = (card: VisualCard, index: number) => {
    switch (card.type) {
      case 'summary_card':
        return renderSummaryCard(card, index)
      case 'chart':
        return renderChart(card, index)
      case 'table':
        return renderTable(card, index)
      case 'map':
        return renderMap(card, index)
      case 'network_graph':
        return renderNetworkGraph(card, index)
      case 'narrative':
        return renderNarrative(card, index)
      default:
        return null
    }
  }

  // Enhanced renderCard with lazy loading support
  const renderCardWithLazyLoading = (card: VisualCard, index: number) => {
    if (shouldLazyLoad(card)) {
      return (
        <Suspense
          key={`${card.type}-${index}`}
          fallback={
            <div className="h-64 bg-synrgy-surface/20 border border-synrgy-primary/10 rounded-xl animate-pulse flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-synrgy-primary animate-spin" />
            </div>
          }
        >
          {renderCard(card, index)}
        </Suspense>
      )
    }
    return renderCard(card, index)
  }

  // Handle composite payloads (multiple cards)
  if (isComposite) {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Summary cards in a grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards
            .filter(card => card.type === 'summary_card')
            .map((card, index) => renderCardWithLazyLoading(card, index))}
        </div>

        {/* Charts and tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {cards
            .filter(card => card.type !== 'summary_card')
            .map((card, index) => renderCardWithLazyLoading(card, index))}
        </div>
        
        {/* Development performance metrics */}
        {import.meta.env.DEV && (
          <div className="mt-4 p-3 bg-synrgy-bg-900/10 border border-synrgy-primary/5 rounded-lg text-xs">
            <div className="flex items-center gap-4 text-synrgy-muted">
              <span>Performance:</span>
              <span>Cache: {getMetrics().cacheSize} entries</span>
              <span>Avg Render: {getMetrics().averageRenderTime.toFixed(2)}ms</span>
              <span>Cache Hit Rate: {((getMetrics().cacheHits / (getMetrics().cacheHits + getMetrics().cacheMisses)) * 100 || 0).toFixed(1)}%</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Handle single card payloads
  return (
    <div className={`${className}`}>
      {renderCardWithLazyLoading(cards[0], 0)}
      {/* Development performance metrics */}
      {import.meta.env.DEV && (
        <div className="mt-4 p-3 bg-synrgy-bg-900/10 border border-synrgy-primary/5 rounded-lg text-xs">
          <div className="flex items-center gap-4 text-synrgy-muted">
            <span>Performance:</span>
            <span>Cache: {getMetrics().cacheSize} entries</span>
            <span>Avg Render: {getMetrics().averageRenderTime.toFixed(2)}ms</span>
            <span>Cache Hit Rate: {((getMetrics().cacheHits / (getMetrics().cacheHits + getMetrics().cacheMisses)) * 100 || 0).toFixed(1)}%</span>
          </div>
        </div>
      )}
    </div>
  )
}
