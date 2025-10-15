/**
 * SYNRGY Visual Payload System
 * Core interfaces for visual-first chat responses
 * Based on SYNRGY.TXT lines 154-170
 */

export interface VisualPayload {
  type: 'composite' | 'chart' | 'table' | 'map' | 'narrative' | 'network_graph' | 'summary_card' | 'insight_feed' | 'metric_gauge' | 'alert_feed'
  cards?: VisualCard[]
  metadata?: {
    query: string
    dsl?: any
    kql?: string
    confidence: number
    execution_time: number
    results_count?: number
    time_range?: {
      start: string
      end: string
    }
  }
}

export interface VisualCard {
  type: 'summary_card' | 'chart' | 'table' | 'map' | 'network_graph' | 'narrative' | 'insight_feed' | 'metric_gauge' | 'alert_feed'
  title?: string
  subtitle?: string
  data?: any
  value?: number | string
  trend?: 'up' | 'down' | 'stable'
  status?: 'success' | 'warning' | 'error' | 'info'
  metadata?: {
    query?: string
    time_range?: {
      start: string
      end: string
    }
    confidence?: number
    execution_time?: number
    [key: string]: any
  }

  // Chart specific
  chart_type?: 'timeseries' | 'bar' | 'pie' | 'scatter' | 'heatmap' | 'line' | 'area'
  x_axis?: string
  y_axis?: string

  // Table specific
  columns?: Array<{
    key: string
    label: string
    type?: 'string' | 'number' | 'date' | 'ip' | 'url'
    sortable?: boolean
    filterable?: boolean
  }>
  rows?: Array<any[]>
  pagination?: {
    total: number
    page: number
    per_page: number
  }

  // Map specific
  locations?: Array<{
    lat: number
    lng: number
    value: number
    label: string
    country?: string
    city?: string
  }>

  // Network graph specific
  nodes?: Array<{
    id: string
    label: string
    type?: string
    size?: number
    color?: string
  }>
  edges?: Array<{
    source: string
    target: string
    label?: string
    weight?: number
  }>

  // Interaction config
  config?: {
    interactive?: boolean
    exportable?: boolean
    pinnable?: boolean
    drilldown?: boolean
    clickable?: boolean
    hoverable?: boolean
    // Chart specific config
    x_field?: string
    y_field?: string
    color?: string
    strokeWidth?: number
    outerRadius?: number
    confidence?: number
    // Gauge specific config
    max?: number
    unit?: string
    size?: 'sm' | 'md' | 'lg'
    critical?: number
    warning?: number
    // Alert feed specific config
    limit?: number
    compact?: boolean
    autoScroll?: boolean
    showTimestamps?: boolean
  }

  // Actions
  actions?: Array<{
    type: 'filter' | 'drilldown' | 'export' | 'investigate' | 'pin'
    label: string
    handler?: string // API endpoint or action type
    context?: any
  }>
}

// Summary card specific interface
export interface SummaryCard extends VisualCard {
  type: 'summary_card'
  value: number | string
  unit?: string
  comparison?: {
    previous: number | string
    change: number
    period: string
  }
  sparkline?: Array<{ x: string; y: number }>
  icon?: string
  color?: 'primary' | 'accent' | 'success' | 'warning' | 'error'
}

// Chart specific interface
export interface ChartCard extends VisualCard {
  type: 'chart'
  chart_type: 'timeseries' | 'bar' | 'pie' | 'scatter' | 'heatmap' | 'line' | 'area'
  data: Array<any>
  axes?: {
    x: { label: string; type: 'datetime' | 'category' | 'number' }
    y: { label: string; type: 'number' | 'percentage' }
  }
  series?: Array<{
    name: string
    color?: string
    type?: string
  }>
}

// Table specific interface
export interface TableCard extends VisualCard {
  type: 'table'
  columns: Array<{
    key: string
    label: string
    type?: 'string' | 'number' | 'date' | 'ip' | 'url'
    sortable?: boolean
    filterable?: boolean
    width?: number
  }>
  rows: Array<any[]>
  sortBy?: {
    column: string
    direction: 'asc' | 'desc'
  }
  filters?: Record<string, any>
}

// Context bridge for dashboard-chat sync
export interface WidgetContext {
  id: string
  type: string
  title: string
  timeRange?: {
    start: string
    end: string
  }
  filters?: Record<string, any>
  clickedRegion?: {
    x: number
    y: number
    data: any
  }
  metadata?: Record<string, any>
}

// Pin to dashboard configuration
export interface PinToDashboardConfig {
  widgetType: VisualCard['type']
  title: string
  data: any
  position?: {
    x: number
    y: number
    w: number
    h: number
  }
  refreshInterval?: number
  filters?: Record<string, any>
}

// Export interfaces
export interface ExportConfig {
  format: 'png' | 'svg' | 'pdf' | 'csv' | 'json'
  filename?: string
  options?: {
    width?: number
    height?: number
    quality?: number
  }
}

// Error handling for visuals
export interface VisualError {
  type: 'data_error' | 'render_error' | 'config_error'
  message: string
  details?: any
  recoverable?: boolean
}

// Visual renderer props
export interface VisualRendererProps {
  payload: VisualPayload
  className?: string
  onPin?: (config: PinToDashboardConfig) => void
  onExport?: (config: ExportConfig) => void
  onAction?: (action: string, context: any) => void
  onError?: (error: VisualError) => void
  interactive?: boolean
  compact?: boolean
}
