/**
 * SYNRGY Enhanced VisualRenderer - Complete Backend Integration
 * Handles all visual_payload types from sophisticated backend
 * Based on SYNRGY.TXT specification
 */

import { useState, useCallback } from 'react'
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

import type { VisualPayload, VisualCard } from '@/types'

interface VisualRendererProps {
  payload: VisualPayload
  className?: string
  onPin?: (card: VisualCard) => void
  onExport?: (card: VisualCard) => void
  interactive?: boolean
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
const TableRenderer = ({ card }: { card: VisualCard }) => {
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
}

/**
 * Narrative/Summary renderer for AI-generated text
 */
const NarrativeRenderer = ({ card }: { card: VisualCard }) => {
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
}

export default function EnhancedVisualRenderer({
  payload,
  className = '',
  onPin,
  onExport,
  interactive = true,
}: VisualRendererProps) {
  const [expandedCard, setExpandedCard] = useState<string | null>(null)
  const [showMetadata, setShowMetadata] = useState(false)

  if (!payload) return null

  // Handle composite payload with multiple cards
  const cards = payload.cards || [payload as VisualCard]
  const isComposite = payload.type === 'composite' && payload.cards && payload.cards.length > 0

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

  const renderSummaryCard = (card: VisualCard, index: number) => (
    <motion.div
      key={`summary-${index}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="relative group bg-synrgy-surface/50 border border-synrgy-primary/20 rounded-xl p-6 hover:border-synrgy-primary/40 transition-all duration-200"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-synrgy-primary rounded-full" />
          <h3 className="text-sm font-medium text-synrgy-muted">{card.title}</h3>
        </div>
      </div>

      <div className="text-3xl font-bold text-synrgy-text mb-1">
        {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
      </div>

      {/* Status indicator */}
      {card.status && (
        <div
          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
            card.status === 'success'
              ? 'bg-green-500/20 text-green-400'
              : card.status === 'warning'
                ? 'bg-yellow-500/20 text-yellow-400'
                : card.status === 'error'
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-synrgy-primary/20 text-synrgy-primary'
          }`}
        >
          {card.status === 'success' && <CheckCircle className="w-3 h-3" />}
          {card.status === 'warning' && <AlertTriangle className="w-3 h-3" />}
          {card.status === 'error' && <AlertTriangle className="w-3 h-3" />}
          {card.status}
        </div>
      )}

      {/* Trend indicator */}
      {card.trend && (
        <div className="flex items-center gap-1 text-xs mt-2">
          {card.trend === 'up' ? (
            <TrendingUp className="w-3 h-3 text-green-500" />
          ) : card.trend === 'down' ? (
            <TrendingDown className="w-3 h-3 text-red-500" />
          ) : (
            <div className="w-3 h-1 bg-synrgy-muted rounded-full" />
          )}
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

    // Process data with dynamic field mapping
    const processedData = card.data.map((item: any) => ({
      ...item,
      x: item[xField] || item.x,
      y: item[yField] || item.y,
      name: item.name || item[xField] || item.x,
      value: item.value || item[yField] || item.y,
    }))

    let chartBody: JSX.Element | null = null

    // Enhanced chart type support
    switch (card.chart_type) {
      case 'bar':
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
        break

      case 'line':
      case 'timeseries':
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
        break

      case 'area':
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
              dataKey="y"
              stroke={config.color || '#00EFFF'}
              fillOpacity={1}
              fill={`url(#${gradientId})`}
            />
          </AreaChart>
        )
        break

      case 'pie':
        chartBody = (
          <RechartsPieChart>
            <Pie
              data={processedData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {processedData.map((_entry: any, index: number) => (
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
        )
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

        <div className={isExpanded ? 'h-96' : 'h-48'}>
          <ResponsiveContainer width="100%" height="100%">
            {chartBody}
          </ResponsiveContainer>
        </div>

        {card.data && card.data.length > 0 && (
          <div className="mt-2 text-xs text-synrgy-muted">{card.data.length} data points</div>
        )}
      </motion.div>
    )
  }

  // Render individual card based on type
  const renderCard = (card: VisualCard, index: number) => {
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
  }

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

      {/* Render cards */}
      {isComposite ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cards.map((card, index) => renderCard(card, index))}
        </div>
      ) : (
        <div className="space-y-4">{cards.map((card, index) => renderCard(card, index))}</div>
      )}

      {cards.length === 0 && (
        <div className="text-center py-8 text-synrgy-muted">
          <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No visualization data available</p>
        </div>
      )}
    </div>
  )
}
