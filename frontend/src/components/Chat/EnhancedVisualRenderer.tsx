/**
 * SYNRGY Enhanced VisualRenderer - Complete Backend Integration
 * Handles all visual_payload types from sophisticated backend
 * Based on SYNRGY.TXT specification
 */

import { useState, useCallback, memo, useMemo, Suspense } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  BarChart3,
  MapPin,
  Globe,
  Maximize2,
  Pin,
  Download,
  Code,
  Eye,
  Loader2,
  Gauge,
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
import GaugeChart from '@/components/Charts/GaugeChart'
import AlertFeed from '@/components/Charts/AlertFeed'

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

/**
 * Enhanced table renderer for backend table data
 */
const TableRenderer = memo(({ card }: { card: VisualCard }) => {
  if (!card.columns || !card.rows) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl overflow-hidden"
    >
      <div className="px-4 py-3 border-b border-synrgy-primary/10 bg-synrgy-bg-900/20">
        <h3 className="text-sm font-medium text-synrgy-text">{card.title || 'Data Table'}</h3>
      </div>

      <div className="overflow-x-auto max-h-64">
        <table className="w-full text-sm">
          <thead className="bg-synrgy-bg-900/50 sticky top-0">
            <tr>
              {card.columns.map((col: any, idx: number) => (
                <th
                  key={idx}
                  className="px-4 py-2 text-left text-synrgy-muted font-medium border-b border-synrgy-primary/10"
                >
                  {col.label || col.key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {card.rows.slice(0, 10).map((row: any[], idx: number) => (
              <tr key={idx} className="hover:bg-synrgy-primary/5 transition-colors">
                {row.map((cell: any, cellIdx: number) => (
                  <td
                    key={cellIdx}
                    className="px-4 py-2 text-synrgy-text border-b border-synrgy-primary/5"
                  >
                    {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {card.rows.length > 10 && (
        <div className="px-4 py-2 text-xs text-synrgy-muted bg-synrgy-bg-900/20 border-t border-synrgy-primary/10">
          Showing 10 of {card.rows.length} results
        </div>
      )}
    </motion.div>
  )
})

/**
 * Narrative/Summary renderer for AI-generated text
 */
const NarrativeRenderer = memo(({ card }: { card: VisualCard }) => {
  if (!card.data && !card.title && !card.value) return null

  const content =
    typeof card.data === 'string'
      ? card.data
      : typeof card.value === 'string'
        ? card.value
        : 'No summary available.'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-synrgy-surface/20 border border-synrgy-accent/20 rounded-xl p-4"
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-synrgy-accent/20 rounded-full flex items-center justify-center mt-1">
          <Info className="w-4 h-4 text-synrgy-accent" />
        </div>
        <div className="flex-1">
          {card.title && <h3 className="font-medium text-synrgy-text mb-2">{card.title}</h3>}
          <div className="text-sm text-synrgy-muted leading-relaxed">{content}</div>
        </div>
      </div>
    </motion.div>
  )
})

// Memoized chart components for better performance
const MemoizedBarChart = memo(({ data, config }: { data: any[], config: any }) => (
  <BarChart data={data}>
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
))

const MemoizedLineChart = memo(({ data, config }: { data: any[], config: any }) => (
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
    <XAxis
      dataKey="x"
      stroke="#94A3B8"
      fontSize={12}
      tick={{ fill: '#94A3B8' }}
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
))

const MemoizedAreaChart = memo(({ data, config, gradientId }: { data: any[], config: any, gradientId: string }) => (
  <AreaChart data={data}>
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
      dataKey="y"
      stroke={config.color || '#00EFFF'}
      fillOpacity={1}
      fill={`url(#${gradientId})`}
    />
  </AreaChart>
))

const MemoizedPieChart = memo(({ data }: { data: any[] }) => (
  <RechartsPieChart>
    <Pie
      data={data}
      cx="50%"
      cy="50%"
      innerRadius={40}
      outerRadius={80}
      paddingAngle={2}
      dataKey="value"
    >
      {data.map((_entry: any, index: number) => (
        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
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
))

export default function EnhancedVisualRenderer({
  payload,
  className = '',
  onPin,
  onExport,
  interactive = true,
  compact = false,
}: VisualRendererProps) {
  const [expandedCard, setExpandedCard] = useState<string | null>(null)
  const [showMetadata, setShowMetadata] = useState(false)
  
  // Performance optimization hook
  const {
    optimizePayload,
    shouldVirtualize,
    shouldLazyLoad,
    startRenderMeasurement,
    endRenderMeasurement,
    getMetrics,
  } = useVisualPerformance({
    cacheEnabled: true,
    virtualizationThreshold: 20,
    performanceTracking: import.meta.env.DEV,
  })

  if (!payload) return null

  // Optimize payload for performance
  const optimizedPayload = useMemo(() => {
    startRenderMeasurement()
    const optimized = optimizePayload(payload)
    endRenderMeasurement()
    return optimized
  }, [payload, optimizePayload, startRenderMeasurement, endRenderMeasurement])

  // Handle composite payload with multiple cards - memoized for performance
  const cards = useMemo(() => optimizedPayload.cards || [optimizedPayload as VisualCard], [optimizedPayload])
  const isComposite = useMemo(() => optimizedPayload.type === 'composite' && optimizedPayload.cards && optimizedPayload.cards.length > 0, [optimizedPayload])
  
  // Virtualization configuration
  const virtualizationConfig = useMemo(() => shouldVirtualize(optimizedPayload), [optimizedPayload, shouldVirtualize])

  const handlePin = useCallback(
    (card: VisualCard) => {
      if (onPin && interactive) {
        onPin(card)
      }
    },
    [onPin, interactive]
  )

  const handleExport = useCallback(
    (card: VisualCard) => {
      if (onExport && interactive) {
        onExport(card)
      }
    },
    [onExport, interactive]
  )

  const renderSummaryCard = useMemo(() => (card: VisualCard, index: number) => {
    // Clean status colors
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'success':
        case 'normal':
          return {
            border: 'border-synrgy-primary/30',
            badge: 'bg-synrgy-primary/15 text-synrgy-primary',
            dot: 'bg-synrgy-primary'
          }
        case 'warning':
          return {
            border: 'border-yellow-500/30',
            badge: 'bg-yellow-500/15 text-yellow-400',
            dot: 'bg-yellow-500'
          }
        case 'critical':
        case 'error':
          return {
            border: 'border-red-500/30',
            badge: 'bg-red-500/15 text-red-400',
            dot: 'bg-red-500'
          }
        default:
          return {
            border: 'border-synrgy-primary/30',
            badge: 'bg-synrgy-primary/15 text-synrgy-primary',
            dot: 'bg-synrgy-primary'
          }
      }
    }

    const statusColor = getStatusColor(card.status || 'normal')

    return (
      <motion.div
        key={`summary-${index}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
        whileHover={{ y: -2, transition: { duration: 0.2 } }}
        className="group relative"
      >
        {/* Clean, modern card */}
        <div className={`
          bg-synrgy-surface/80 backdrop-blur-sm
          border ${statusColor.border}
          rounded-2xl p-8
          shadow-lg hover:shadow-xl
          transition-all duration-300
          min-h-[180px] w-full
        `}>
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 ${statusColor.dot} rounded-full`} />
              <h3 className="text-sm font-semibold text-synrgy-muted uppercase tracking-wide">
                {card.title}
              </h3>
            </div>
          </div>

          {/* Main value */}
          <div className="mb-6">
            <div className="text-4xl font-bold text-synrgy-text">
              {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
            </div>
          </div>

          {/* Status and trend */}
          <div className="flex items-center justify-between">
            {/* Status badge */}
            <div className={`
              inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium
              ${statusColor.badge}
            `}>
              {card.status === 'success' || card.status === 'normal' ? (
                <CheckCircle className="w-3 h-3" />
              ) : card.status === 'warning' ? (
                <AlertTriangle className="w-3 h-3" />
              ) : card.status === 'critical' || card.status === 'error' ? (
                <AlertTriangle className="w-3 h-3" />
              ) : (
                <div className="w-3 h-3 rounded-full bg-current" />
              )}
              {card.status || 'normal'}
            </div>

            {/* Trend indicator */}
            {(card.trend || card.data?.change) && (
              <div className="text-xs text-synrgy-muted">
                {(card.trend === 'up' || card.data?.change?.trend === 'up') ? (
                  <div className="flex items-center gap-1 text-green-400">
                    <TrendingUp className="w-3 h-3" />
                    <span>+{card.data?.change?.value || 0}%</span>
                  </div>
                ) : (card.trend === 'down' || card.data?.change?.trend === 'down') ? (
                  <div className="flex items-center gap-1 text-red-400">
                    <TrendingDown className="w-3 h-3" />
                    <span>-{Math.abs(card.data?.change?.value || 0)}%</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-1 bg-synrgy-muted rounded-full" />
                    <span>stable</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Action button */}
          {interactive && (
            <button
              onClick={() => handlePin(card)}
              className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-3 right-3 p-2 bg-synrgy-primary/20 hover:bg-synrgy-primary/30 rounded-lg text-synrgy-primary"
              title="Pin to Dashboard"
            >
              <Pin className="w-3 h-3" />
            </button>
          )}
        </div>
      </motion.div>
    )
  }, [handlePin, interactive])

  const renderChart = useCallback((card: VisualCard, index: number) => {
    if (!card.data || !Array.isArray(card.data)) return null

    const isExpanded = expandedCard === `chart-${index}`

    // Dynamic field mapping from config
    const config = card.config || {}
    const xField = config.x_field || 'x'
    const yField = config.y_field || 'y'

    // Process data with dynamic field mapping - memoized for performance
    const processedData = useMemo(() => card.data.map((item: any) => ({
      ...item,
      x: item[xField] || item.x,
      y: item[yField] || item.y,
      name: item.name || item[xField] || item.x,
      value: item.value || item[yField] || item.y,
    })), [card.data, xField, yField])

    let chartBody: JSX.Element | null = null

    // Enhanced chart type support with memoized components
    switch (card.chart_type) {
      case 'bar':
        chartBody = <MemoizedBarChart data={processedData} config={config} />
        break

      case 'line':
      case 'timeseries':
        chartBody = <MemoizedLineChart data={processedData} config={config} />
        break

      case 'area':
        const gradientId = `gradient-${index}`
        chartBody = <MemoizedAreaChart data={processedData} config={config} gradientId={gradientId} />
        break

      case 'pie':
        chartBody = <MemoizedPieChart data={processedData} />
        break

      default:
        chartBody = (
          <div className="h-full flex items-center justify-center text-synrgy-muted">
            Unsupported chart type: {card.chart_type}
          </div>
        )
    }

    return (
      <motion.div
        key={`chart-${index}`}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className={`relative group bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4 ${
          isExpanded ? 'col-span-full' : ''
        } hover:border-synrgy-primary/40 transition-all duration-200`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-synrgy-primary" />
            <h3 className="font-medium text-synrgy-text">{card.title || 'Chart'}</h3>
            {config.confidence && (
              <span className="text-xs px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded">
                {(config.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
          </div>
          {interactive && (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
              <button
                onClick={() => setExpandedCard(isExpanded ? null : `chart-${index}`)}
                className="p-1 bg-synrgy-muted/20 hover:bg-synrgy-muted/30 rounded text-synrgy-muted"
                title="Expand"
              >
                <Maximize2 className="w-3 h-3" />
              </button>
              <button
                onClick={() => handlePin(card)}
                className="p-1 bg-synrgy-primary/20 hover:bg-synrgy-primary/30 rounded text-synrgy-primary"
                title="Pin to Dashboard"
              >
                <Pin className="w-3 h-3" />
              </button>
              <button
                onClick={() => handleExport(card)}
                className="p-1 bg-synrgy-accent/20 hover:bg-synrgy-accent/30 rounded text-synrgy-accent"
                title="Export"
              >
                <Download className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        <div className={`w-full ${isExpanded ? 'h-[500px]' : 'h-[320px]'}`}>
          <ResponsiveContainer width="100%" height="100%">
            {chartBody}
          </ResponsiveContainer>
        </div>

        {card.data && card.data.length > 0 && (
          <div className="mt-2 text-xs text-synrgy-muted">{card.data.length} data points</div>
        )}
      </motion.div>
    )
  }, [expandedCard, handlePin, handleExport, interactive])

  // Render individual card based on type with lazy loading support
  const renderCard = useCallback((card: VisualCard, index: number) => {
    switch (card.type) {
      case 'summary_card':
        return renderSummaryCard(card, index)
      case 'chart':
        return renderChart(card, index)
      case 'table':
        return <TableRenderer key={`table-${index}`} card={card} />
      case 'narrative':
        return <NarrativeRenderer key={`narrative-${index}`} card={card} />
      case 'map':
        return (
          <motion.div
            key={`map-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-synrgy-primary" />
              <h3 className="font-medium text-synrgy-text">{card.title || 'Geographic Data'}</h3>
            </div>
            <div className="h-48 bg-synrgy-bg-900/50 rounded border border-synrgy-primary/10 flex items-center justify-center">
              <span className="text-synrgy-muted">Map visualization (requires implementation)</span>
            </div>
          </motion.div>
        )
      case 'metric_gauge':
        return (
          <motion.div
            key={`gauge-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <Gauge className="w-4 h-4 text-synrgy-primary" />
              <h3 className="font-medium text-synrgy-text">{card.title || 'Metric Gauge'}</h3>
            </div>
            <div className="flex justify-center">
              <GaugeChart
                value={typeof card.value === 'number' ? card.value : 0}
                max={card.config?.max || 100}
                title={card.title || 'Metric'}
                unit={card.config?.unit || '%'}
                size={card.config?.size || 'md'}
                critical={card.config?.critical || 80}
                warning={card.config?.warning || 60}
              />
            </div>
          </motion.div>
        )
      case 'alert_feed':
        return (
          <motion.div
            key={`alerts-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4"
          >
            <AlertFeed
              alerts={card.data || []}
              maxVisible={card.config?.limit || 10}
              compact={card.config?.compact || false}
              autoScroll={card.config?.autoScroll !== false}
              showTimestamps={card.config?.showTimestamps !== false}
            />
          </motion.div>
        )
      case 'network_graph':
        return (
          <motion.div
            key={`network-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <Globe className="w-4 h-4 text-synrgy-primary" />
              <h3 className="font-medium text-synrgy-text">{card.title || 'Network Graph'}</h3>
            </div>
            <div className="h-48 bg-synrgy-bg-900/50 rounded border border-synrgy-primary/10 flex items-center justify-center">
              <span className="text-synrgy-muted">
                Network visualization (requires implementation)
              </span>
            </div>
          </motion.div>
        )
      default:
        return (
          <motion.div
            key={`unknown-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              <span className="text-orange-500 text-sm">
                Unknown visualization type: {card.type}
              </span>
            </div>
          </motion.div>
        )
    }
  }, [renderSummaryCard, renderChart])

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Metadata header */}
      {payload.metadata && (
        <div className="bg-synrgy-bg-900/20 border border-synrgy-primary/10 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-synrgy-muted">
              <Code className="w-4 h-4" />
              <span>Query executed in {payload.metadata.execution_time || 0}ms</span>
              {payload.metadata.confidence && (
                <span className="text-synrgy-primary">
                  • {(payload.metadata.confidence * 100).toFixed(0)}% confidence
                </span>
              )}
              {payload.metadata.results_count !== undefined && (
                <span>• {payload.metadata.results_count} results</span>
              )}
            </div>
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className="text-synrgy-muted hover:text-synrgy-primary transition-colors"
            >
              <Eye className="w-4 h-4" />
            </button>
          </div>

          <AnimatePresence>
            {showMetadata && payload.metadata && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-synrgy-primary/10"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  {payload.metadata.query && (
                    <div>
                      <span className="text-synrgy-accent font-medium">Original Query:</span>
                      <div className="mt-1 p-2 bg-synrgy-surface/30 rounded text-synrgy-text">
                        {payload.metadata.query}
                      </div>
                    </div>
                  )}
                  {payload.metadata.kql && (
                    <div>
                      <span className="text-synrgy-accent font-medium">KQL:</span>
                      <div className="mt-1 p-2 bg-synrgy-surface/30 rounded text-synrgy-text font-mono">
                        {payload.metadata.kql}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Render cards with performance optimization */}
      {isComposite ? (
        <div className="w-full">
          {virtualizationConfig.enabled ? (
            // Virtual scrolling for large datasets
            <div className="w-full space-y-6">
              {cards
                .slice(0, virtualizationConfig.chunkSize)
                .map((card, index) => 
                  shouldLazyLoad(card) ? (
                    <Suspense 
                      key={`${card.type}-${index}`}
                      fallback={
                        <div className="h-48 bg-synrgy-surface/20 border border-synrgy-primary/10 rounded-xl animate-pulse flex items-center justify-center">
                          <Loader2 className="w-8 h-8 text-synrgy-primary animate-spin" />
                        </div>
                      }
                    >
                      {renderCard(card, index)}
                    </Suspense>
                  ) : (
                    renderCard(card, index)
                  )
                )}
              {cards.length > virtualizationConfig.chunkSize && (
                <div className="text-center py-6">
                  <span className="text-sm text-synrgy-muted">
                    Showing {virtualizationConfig.chunkSize} of {cards.length} items
                    {import.meta.env.DEV && (
                      <span className="ml-2 text-xs opacity-75">
                        (Performance optimized)
                      </span>
                    )}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="w-full space-y-6">
              {cards.map((card, index) => 
                shouldLazyLoad(card) ? (
                  <Suspense 
                    key={`${card.type}-${index}`}
                    fallback={
                      <div className="h-48 bg-synrgy-surface/20 border border-synrgy-primary/10 rounded-xl animate-pulse flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-synrgy-primary animate-spin" />
                      </div>
                    }
                  >
                    {renderCard(card, index)}
                  </Suspense>
                ) : (
                  renderCard(card, index)
                )
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="w-full space-y-6">
          {cards.map((card, index) => 
            shouldLazyLoad(card) ? (
              <Suspense 
                key={`${card.type}-${index}`}
                fallback={
                  <div className="h-48 bg-synrgy-surface/20 border border-synrgy-primary/10 rounded-xl animate-pulse flex items-center justify-center">
                    <Loader2 className="w-8 h-8 text-synrgy-primary animate-spin" />
                  </div>
                }
              >
                {renderCard(card, index)}
              </Suspense>
            ) : (
              renderCard(card, index)
            )
          )}
        </div>
      )}

      {cards.length === 0 && (
        <div className="text-center py-8 text-synrgy-muted">
          <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No visualization data available</p>
        </div>
      )}
      
      {/* Development performance metrics */}
      {import.meta.env.DEV && (
        <div className="mt-4 p-3 bg-synrgy-bg-900/10 border border-synrgy-primary/5 rounded-lg text-xs">
          <div className="flex items-center gap-4 text-synrgy-muted">
            <span>Performance:</span>
            <span>Cache: {getMetrics().cacheSize} entries</span>
            <span>Avg Render: {getMetrics().averageRenderTime.toFixed(2)}ms</span>
            <span>Cache Hit Rate: {((getMetrics().cacheHits / (getMetrics().cacheHits + getMetrics().cacheMisses)) * 100 || 0).toFixed(1)}%</span>
            {virtualizationConfig.enabled && <span className="text-synrgy-accent">Virtualized</span>}
          </div>
        </div>
      )}
    </div>
  )
}
