/**
 * Advanced Interactive Visual Renderer for SYNRGY
 * Enhanced version with drill-down, filtering, context menus, and advanced interactions
 */

import React, { useState, useCallback, memo, useMemo, useRef } from 'react'
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
  Filter,
  Search,
  ZoomIn,
  MoreHorizontal,
  ChevronDown,
  ExternalLink,
  Layers,
  Target,
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
  ReferenceLine,
} from 'recharts'

import type { VisualPayload, VisualCard } from '@/types'

interface AdvancedInteractiveRendererProps {
  payload: VisualPayload
  className?: string
  onPin?: (card: VisualCard) => void
  onExport?: (card: VisualCard) => void
  onDrilldown?: (context: DrilldownContext) => void
  onFilter?: (filter: FilterContext) => void
  interactive?: boolean
}

interface DrilldownContext {
  level: number
  data: any
  originalQuery: string
  timeRange?: any
  filters?: any[]
  path: string[]
}

interface FilterContext {
  field: string
  operator: string
  value: any
  displayName: string
}

interface ContextMenuState {
  show: boolean
  x: number
  y: number
  data: any
  actions: ContextAction[]
}

interface ContextAction {
  label: string
  icon: React.ComponentType<{ className?: string }>
  action: () => void
  disabled?: boolean
}

// Enhanced color palette with semantic meanings
const SEMANTIC_COLORS = {
  primary: '#00EFFF',
  accent: '#FF7A00',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6',
  chart: ['#00EFFF', '#FF7A00', '#22D3EE', '#F97316', '#06B6D4', '#EA580C', '#0891B2', '#C2410C'],
}

/**
 * Advanced Chart Component with Interactions
 */
const InteractiveChart = memo(({ 
  card, 
  index, 
  onDrilldown, 
  onFilter,
  onPin,
  onExport 
}: {
  card: VisualCard
  index: number
  onDrilldown?: (context: DrilldownContext) => void
  onFilter?: (filter: FilterContext) => void
  onPin?: (card: VisualCard) => void
  onExport?: (card: VisualCard) => void
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [contextMenu, setContextMenu] = useState<ContextMenuState>({ 
    show: false, 
    x: 0, 
    y: 0, 
    data: null, 
    actions: [] 
  })
  const [selectedDataPoints, setSelectedDataPoints] = useState<any[]>([])
  const [filterPath, setFilterPath] = useState<string[]>([])
  const chartRef = useRef<HTMLDivElement>(null)

  const config = card.config || {}
  const xField = config.x_field || 'x'
  const yField = config.y_field || 'y'

  // Enhanced data processing with filter support
  const processedData = useMemo(() => {
    if (!card.data || !Array.isArray(card.data)) return []
    
    return card.data.map((item: any, idx: number) => ({
      ...item,
      x: item[xField] || item.x,
      y: item[yField] || item.y,
      name: item.name || item[xField] || item.x,
      value: item.value || item[yField] || item.y,
      originalIndex: idx,
      isSelected: selectedDataPoints.includes(idx),
    }))
  }, [card.data, xField, yField, selectedDataPoints])

  // Handle chart element clicks
  const handleChartClick = useCallback((data: any, index: number, event: any) => {
    if (!data) return

    const rect = chartRef.current?.getBoundingClientRect()
    if (!rect) return

    const contextActions: ContextAction[] = [
      {
        label: 'Drill Down',
        icon: ZoomIn,
        action: () => {
          if (onDrilldown) {
            onDrilldown({
              level: filterPath.length + 1,
              data,
              originalQuery: card.metadata?.query || '',
              timeRange: card.metadata?.time_range,
              filters: [],
              path: [...filterPath, data.name || data.x]
            })
          }
          setContextMenu(prev => ({ ...prev, show: false }))
        },
        disabled: !onDrilldown
      },
      {
        label: 'Filter by this value',
        icon: Filter,
        action: () => {
          if (onFilter) {
            onFilter({
              field: xField,
              operator: 'equals',
              value: data.x,
              displayName: `${xField} = ${data.x}`
            })
          }
          setContextMenu(prev => ({ ...prev, show: false }))
        },
        disabled: !onFilter
      },
      {
        label: 'Investigate',
        icon: Target,
        action: () => {
          // Open investigation context
          console.log('Opening investigation for:', data)
          setContextMenu(prev => ({ ...prev, show: false }))
        }
      },
      {
        label: 'Export Data Point',
        icon: ExternalLink,
        action: () => {
          // Export single data point
          const dataToExport = {
            point: data,
            context: { card: card.title, timestamp: new Date().toISOString() }
          }
          const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `synrgy-datapoint-${data.x || 'unknown'}.json`
          a.click()
          URL.revokeObjectURL(url)
          setContextMenu(prev => ({ ...prev, show: false }))
        }
      }
    ]

    setContextMenu({
      show: true,
      x: event.clientX,
      y: event.clientY,
      data,
      actions: contextActions
    })
  }, [filterPath, onDrilldown, onFilter, xField, card.metadata, card.title])

  // Enhanced tooltip content
  const CustomTooltip = useCallback(({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload
    
    return (
      <div className="bg-synrgy-surface border border-synrgy-primary/20 rounded-lg p-3 shadow-xl">
        <div className="text-synrgy-text font-medium mb-2">{label}</div>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between gap-4">
            <span className="text-synrgy-muted">Value:</span>
            <span className="text-synrgy-accent font-medium">
              {typeof payload[0].value === 'number' 
                ? payload[0].value.toLocaleString() 
                : payload[0].value}
            </span>
          </div>
          {data.category && (
            <div className="flex justify-between gap-4">
              <span className="text-synrgy-muted">Category:</span>
              <span className="text-synrgy-text">{data.category}</span>
            </div>
          )}
          {data.trend && (
            <div className="flex justify-between gap-4">
              <span className="text-synrgy-muted">Trend:</span>
              <div className="flex items-center gap-1">
                {data.trend === 'up' ? (
                  <TrendingUp className="w-3 h-3 text-green-500" />
                ) : data.trend === 'down' ? (
                  <TrendingDown className="w-3 h-3 text-red-500" />
                ) : null}
                <span className={`capitalize ${
                  data.trend === 'up' ? 'text-green-500' : 
                  data.trend === 'down' ? 'text-red-500' : 'text-synrgy-text'
                }`}>{data.trend}</span>
              </div>
            </div>
          )}
        </div>
        <div className="mt-2 pt-2 border-t border-synrgy-primary/10 text-xs text-synrgy-muted">
          Click for options
        </div>
      </div>
    )
  }, [])

  // Generate chart component based on type
  const renderChartBody = useMemo(() => {
    const commonProps = {
      data: processedData,
      onClick: handleChartClick
    }

    switch (card.chart_type) {
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
            <XAxis 
              dataKey="x" 
              stroke="#94A3B8" 
              fontSize={12} 
              tick={{ fill: '#94A3B8' }}
              angle={processedData.length > 10 ? -45 : 0}
              textAnchor={processedData.length > 10 ? 'end' : 'middle'}
              height={processedData.length > 10 ? 80 : 60}
            />
            <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="y" 
              fill={config.color || SEMANTIC_COLORS.primary}
              radius={[4, 4, 0, 0]}
              cursor="pointer"
              onMouseEnter={(data, index) => {
                // Highlight related data points
                setSelectedDataPoints([index])
              }}
              onMouseLeave={() => {
                setSelectedDataPoints([])
              }}
            />
            {/* Add reference line for average */}
            {processedData.length > 0 && (
              <ReferenceLine 
                y={processedData.reduce((sum, item) => sum + (item.y || 0), 0) / processedData.length}
                stroke={SEMANTIC_COLORS.warning}
                strokeDasharray="5 5"
                label={{ value: "Avg", position: "insideTopRight" }}
              />
            )}
          </BarChart>
        )

      case 'line':
      case 'timeseries':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
            <XAxis 
              dataKey="x" 
              stroke="#94A3B8" 
              fontSize={12} 
              tick={{ fill: '#94A3B8' }}
            />
            <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="y"
              stroke={config.color || SEMANTIC_COLORS.primary}
              strokeWidth={3}
              dot={{ 
                fill: config.color || SEMANTIC_COLORS.primary, 
                strokeWidth: 2, 
                r: 4,
                cursor: 'pointer'
              }}
              activeDot={{ 
                r: 6, 
                fill: SEMANTIC_COLORS.accent,
                cursor: 'pointer'
              }}
            />
          </LineChart>
        )

      case 'area':
        const gradientId = `gradient-${index}`
        return (
          <AreaChart {...commonProps}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={config.color || SEMANTIC_COLORS.primary} stopOpacity={0.8} />
                <stop offset="95%" stopColor={config.color || SEMANTIC_COLORS.primary} stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
            <XAxis dataKey="x" stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
            <YAxis stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="y"
              stroke={config.color || SEMANTIC_COLORS.primary}
              strokeWidth={2}
              fillOpacity={1}
              fill={`url(#${gradientId})`}
              cursor="pointer"
            />
          </AreaChart>
        )

      case 'pie':
        return (
          <RechartsPieChart>
            <Pie
              data={processedData}
              cx="50%"
              cy="50%"
              innerRadius={isExpanded ? 60 : 40}
              outerRadius={isExpanded ? 120 : 80}
              paddingAngle={2}
              dataKey="value"
              onClick={handleChartClick}
              cursor="pointer"
            >
              {processedData.map((_entry: any, idx: number) => (
                <Cell 
                  key={`cell-${idx}`} 
                  fill={SEMANTIC_COLORS.chart[idx % SEMANTIC_COLORS.chart.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </RechartsPieChart>
        )

      default:
        return (
          <div className="h-full flex items-center justify-center text-synrgy-muted">
            <div className="text-center">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
              <p>Unsupported chart type: {card.chart_type}</p>
            </div>
          </div>
        )
    }
  }, [card.chart_type, processedData, config, index, isExpanded, handleChartClick, CustomTooltip])

  return (
    <>
      <motion.div
        ref={chartRef}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
        className={`relative group bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4 ${
          isExpanded ? 'col-span-full z-10' : ''
        } hover:border-synrgy-primary/40 transition-all duration-200`}
      >
        {/* Enhanced Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-synrgy-primary" />
              <h3 className="font-medium text-synrgy-text">{card.title || 'Chart'}</h3>
            </div>
            
            {/* Filter breadcrumbs */}
            {filterPath.length > 0 && (
              <div className="flex items-center gap-1 text-xs">
                {filterPath.map((filter, idx) => (
                  <React.Fragment key={idx}>
                    <ChevronDown className="w-3 h-3 text-synrgy-muted rotate-270" />
                    <span className="px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded">
                      {filter}
                    </span>
                  </React.Fragment>
                ))}
              </div>
            )}

            {config.confidence && (
              <span className="text-xs px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded">
                {(config.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 opacity-0 group-hover:opacity-100 hover:bg-synrgy-muted/10 rounded-lg transition-all"
              title={isExpanded ? 'Minimize' : 'Expand'}
            >
              <Maximize2 className="w-4 h-4 text-synrgy-muted" />
            </button>
            
            <button
              onClick={() => onPin?.(card)}
              className="p-2 opacity-0 group-hover:opacity-100 hover:bg-synrgy-primary/10 rounded-lg transition-all"
              title="Pin to Dashboard"
            >
              <Pin className="w-4 h-4 text-synrgy-primary" />
            </button>
            
            <button
              onClick={() => onExport?.(card)}
              className="p-2 opacity-0 group-hover:opacity-100 hover:bg-synrgy-accent/10 rounded-lg transition-all"
              title="Export Chart"
            >
              <Download className="w-4 h-4 text-synrgy-accent" />
            </button>
          </div>
        </div>

        {/* Chart Content */}
        <div className={`${isExpanded ? 'h-96' : 'h-64'} relative`}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChartBody}
          </ResponsiveContainer>
          
          {/* Data overlay */}
          {selectedDataPoints.length > 0 && (
            <div className="absolute top-2 right-2 bg-synrgy-surface border border-synrgy-primary/20 rounded px-2 py-1 text-xs">
              <span className="text-synrgy-muted">Selected: </span>
              <span className="text-synrgy-accent">{selectedDataPoints.length} points</span>
            </div>
          )}
        </div>

        {/* Chart Stats */}
        <div className="mt-3 flex items-center justify-between text-xs text-synrgy-muted">
          <span>{processedData.length} data points</span>
          {processedData.length > 0 && (
            <span>
              Range: {Math.min(...processedData.map(d => d.y || 0))} - {Math.max(...processedData.map(d => d.y || 0))}
            </span>
          )}
        </div>
      </motion.div>

      {/* Context Menu */}
      <AnimatePresence>
        {contextMenu.show && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 z-50" 
              onClick={() => setContextMenu(prev => ({ ...prev, show: false }))}
            />
            
            {/* Menu */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              style={{
                position: 'fixed',
                left: Math.min(contextMenu.x, window.innerWidth - 200),
                top: Math.min(contextMenu.y, window.innerHeight - 200),
                zIndex: 51
              }}
              className="bg-synrgy-surface border border-synrgy-primary/20 rounded-lg shadow-xl py-2 min-w-[180px]"
            >
              {contextMenu.actions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={action.action}
                  disabled={action.disabled}
                  className="w-full px-4 py-2 text-left flex items-center gap-3 hover:bg-synrgy-primary/5 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
                >
                  <action.icon className="w-4 h-4 text-synrgy-muted" />
                  <span className="text-synrgy-text">{action.label}</span>
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
})

/**
 * Advanced Interactive Table with sorting, filtering, and selection
 */
const InteractiveTable = memo(({ 
  card, 
  onFilter, 
  onPin 
}: { 
  card: VisualCard
  onFilter?: (filter: FilterContext) => void
  onPin?: (card: VisualCard) => void 
}) => {
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())

  if (!card.columns || !card.rows) return null

  const filteredRows = useMemo(() => {
    let filtered = card.rows
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(row => 
        row.some(cell => 
          String(cell).toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    // Apply sorting
    if (sortConfig) {
      const columnIndex = card.columns.findIndex(col => col.key === sortConfig.key || col.label === sortConfig.key)
      if (columnIndex !== -1) {
        filtered = [...filtered].sort((a, b) => {
          const aVal = a[columnIndex]
          const bVal = b[columnIndex]
          
          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
          }
          
          const aStr = String(aVal).toLowerCase()
          const bStr = String(bVal).toLowerCase()
          
          if (sortConfig.direction === 'asc') {
            return aStr.localeCompare(bStr)
          } else {
            return bStr.localeCompare(aStr)
          }
        })
      }
    }

    return filtered
  }, [card.rows, card.columns, searchTerm, sortConfig])

  const handleSort = (columnKey: string) => {
    setSortConfig(current => {
      if (current?.key === columnKey) {
        return {
          key: columnKey,
          direction: current.direction === 'asc' ? 'desc' : 'asc'
        }
      }
      return { key: columnKey, direction: 'asc' }
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl overflow-hidden"
    >
      {/* Table Header with Controls */}
      <div className="p-4 border-b border-synrgy-primary/10 bg-synrgy-bg-900/20">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-synrgy-text">{card.title || 'Data Table'}</h3>
          <button
            onClick={() => onPin?.(card)}
            className="p-1 hover:bg-synrgy-primary/10 rounded transition-colors"
            title="Pin to Dashboard"
          >
            <Pin className="w-4 h-4 text-synrgy-primary" />
          </button>
        </div>
        
        {/* Search and Controls */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
            <input
              type="text"
              placeholder="Search in table..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-synrgy-surface border border-synrgy-primary/20 rounded-lg text-synrgy-text placeholder-synrgy-muted focus:outline-none focus:border-synrgy-primary/40 text-sm"
            />
          </div>
          
          {selectedRows.size > 0 && (
            <div className="flex items-center gap-2 text-sm text-synrgy-accent">
              <span>{selectedRows.size} selected</span>
              <button
                onClick={() => {
                  // Handle bulk action
                  console.log('Bulk action on:', Array.from(selectedRows))
                }}
                className="px-2 py-1 bg-synrgy-accent/10 hover:bg-synrgy-accent/20 rounded text-xs transition-colors"
              >
                Actions
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Table */}
      <div className="overflow-x-auto max-h-96">
        <table className="w-full text-sm">
          <thead className="bg-synrgy-bg-900/50 sticky top-0">
            <tr>
              <th className="w-8 px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedRows.size === filteredRows.length && filteredRows.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedRows(new Set(filteredRows.map((_, idx) => idx)))
                    } else {
                      setSelectedRows(new Set())
                    }
                  }}
                  className="w-3 h-3 rounded border-synrgy-primary/30"
                />
              </th>
              {card.columns.map((col: any, idx: number) => (
                <th
                  key={idx}
                  className="px-4 py-3 text-left text-synrgy-muted font-medium border-b border-synrgy-primary/10 cursor-pointer hover:text-synrgy-primary transition-colors"
                  onClick={() => handleSort(col.key || col.label)}
                >
                  <div className="flex items-center gap-2">
                    <span>{col.label || col.key}</span>
                    {sortConfig?.key === (col.key || col.label) && (
                      <div className="flex flex-col">
                        <ChevronDown 
                          className={`w-3 h-3 transition-transform ${
                            sortConfig.direction === 'asc' ? 'rotate-180' : ''
                          }`}
                        />
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.slice(0, 20).map((row: any[], rowIdx: number) => (
              <motion.tr
                key={rowIdx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: rowIdx * 0.02 }}
                className={`hover:bg-synrgy-primary/5 transition-colors ${
                  selectedRows.has(rowIdx) ? 'bg-synrgy-primary/10' : ''
                }`}
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedRows.has(rowIdx)}
                    onChange={(e) => {
                      const newSelected = new Set(selectedRows)
                      if (e.target.checked) {
                        newSelected.add(rowIdx)
                      } else {
                        newSelected.delete(rowIdx)
                      }
                      setSelectedRows(newSelected)
                    }}
                    className="w-3 h-3 rounded border-synrgy-primary/30"
                  />
                </td>
                {row.map((cell: any, cellIdx: number) => (
                  <td
                    key={cellIdx}
                    className="px-4 py-3 text-synrgy-text border-b border-synrgy-primary/5 cursor-pointer hover:text-synrgy-primary transition-colors"
                    onClick={() => {
                      // Handle cell click for filtering
                      if (onFilter && card.columns[cellIdx]) {
                        onFilter({
                          field: card.columns[cellIdx].key || card.columns[cellIdx].label,
                          operator: 'equals',
                          value: cell,
                          displayName: `${card.columns[cellIdx].label} = ${cell}`
                        })
                      }
                    }}
                    title="Click to filter by this value"
                  >
                    {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Table Footer */}
      <div className="px-4 py-3 bg-synrgy-bg-900/20 border-t border-synrgy-primary/10 flex items-center justify-between text-xs text-synrgy-muted">
        <span>
          Showing {Math.min(20, filteredRows.length)} of {filteredRows.length} results
          {searchTerm && ` (filtered from ${card.rows.length} total)`}
        </span>
        {card.rows.length > 20 && (
          <span className="text-synrgy-accent">Pagination coming soon</span>
        )}
      </div>
    </motion.div>
  )
})

export default function AdvancedInteractiveRenderer({
  payload,
  className = '',
  onPin,
  onExport,
  onDrilldown,
  onFilter,
  interactive = true,
}: AdvancedInteractiveRendererProps) {
  const [showMetadata, setShowMetadata] = useState(false)

  if (!payload) return null

  const cards = useMemo(() => payload.cards || [payload as VisualCard], [payload])
  const isComposite = useMemo(() => payload.type === 'composite' && payload.cards && payload.cards.length > 0, [payload])

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

  const renderCard = (card: VisualCard, index: number) => {
    switch (card.type) {
      case 'chart':
        return (
          <InteractiveChart
            key={`chart-${index}`}
            card={card}
            index={index}
            onDrilldown={onDrilldown}
            onFilter={onFilter}
            onPin={handlePin}
            onExport={handleExport}
          />
        )

      case 'table':
        return (
          <InteractiveTable
            key={`table-${index}`}
            card={card}
            onFilter={onFilter}
            onPin={handlePin}
          />
        )

      default:
        // Fallback to enhanced visual renderer for other types
        return (
          <motion.div
            key={`card-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-4"
          >
            <div className="text-center text-synrgy-muted">
              <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Advanced renderer for {card.type} coming soon</p>
            </div>
          </motion.div>
        )
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Enhanced Metadata Display */}
      {payload.metadata && (
        <div className="bg-synrgy-bg-900/20 border border-synrgy-primary/10 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm text-synrgy-muted">
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4" />
                <span>Executed in {payload.metadata.execution_time || 0}ms</span>
              </div>
              
              {payload.metadata.confidence && (
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  <span className="text-synrgy-primary">
                    {(payload.metadata.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
              )}
              
              {payload.metadata.results_count !== undefined && (
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>{payload.metadata.results_count} results</span>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className="p-1 hover:bg-synrgy-primary/10 rounded transition-colors"
              title="Toggle metadata"
            >
              <Eye className="w-4 h-4 text-synrgy-muted" />
            </button>
          </div>

          <AnimatePresence>
            {showMetadata && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-synrgy-primary/10"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  {payload.metadata.query && (
                    <div>
                      <span className="text-synrgy-accent font-medium">Query:</span>
                      <div className="mt-1 p-2 bg-synrgy-surface/30 rounded text-synrgy-text">
                        {payload.metadata.query}
                      </div>
                    </div>
                  )}
                  
                  {payload.metadata.kql && (
                    <div>
                      <span className="text-synrgy-accent font-medium">KQL:</span>
                      <div className="mt-1 p-2 bg-synrgy-surface/30 rounded text-synrgy-text font-mono text-xs">
                        {payload.metadata.kql}
                      </div>
                    </div>
                  )}

                  {payload.metadata.time_range && (
                    <div>
                      <span className="text-synrgy-accent font-medium">Time Range:</span>
                      <div className="mt-1 p-2 bg-synrgy-surface/30 rounded text-synrgy-text">
                        {payload.metadata.time_range.start} to {payload.metadata.time_range.end}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Render Cards */}
      <div className={isComposite ? "grid grid-cols-1 lg:grid-cols-2 gap-6" : "space-y-6"}>
        {cards.map((card, index) => renderCard(card, index))}
      </div>

      {cards.length === 0 && (
        <div className="text-center py-12 text-synrgy-muted">
          <Info className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <h3 className="text-lg font-medium text-synrgy-text mb-2">No Data Available</h3>
          <p>No visualization data was returned for this query.</p>
        </div>
      )}
    </div>
  )
}
