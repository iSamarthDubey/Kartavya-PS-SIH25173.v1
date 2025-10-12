// Core application types for SYNRGY

// ===== Chat & Conversation Types =====
export interface ChatMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    intent?: string
    confidence?: number
    processing_time?: number
    query_type?: string
    [key: string]: any
  }
  visual_payload?: VisualPayload
  error?: string
  status?: 'pending' | 'success' | 'error' | 'clarification_needed'
}

export interface ChatRequest {
  query: string
  conversation_id?: string
  user_context?: Record<string, any>
  filters?: Record<string, any>
  limit?: number
}

export interface ChatResponse {
  conversation_id: string
  query: string
  intent: string
  confidence: number
  entities: Entity[]
  siem_query: Record<string, any>
  results: QueryResult[]
  summary: string
  visualizations?: Visualization[]
  suggestions?: string[]
  metadata: Record<string, any>
  status: string
  error?: string
}

// ===== Visual Payload Types (SYNRGY Enterprise System) =====
export * from './visual'

// ===== Entity & Query Types =====
export interface Entity {
  type: string
  value: string
  confidence?: number
  start?: number
  end?: number
  metadata?: Record<string, any>
}

export interface QueryResult {
  timestamp?: string
  message?: string
  severity?: string
  user?: string
  source_ip?: string
  dest_ip?: string
  host?: string
  threat_name?: string
  threat_type?: string
  outcome?: string
  protocol?: string
  bytes?: number
  file_path?: string
  [key: string]: any
}

// ===== Visualization Types =====
export interface Visualization {
  type: 'time_series' | 'bar_chart' | 'pie_chart' | 'table' | 'map' | 'network_graph'
  title: string
  data: any[]
  config?: {
    x_field?: string
    y_field?: string
    color_field?: string
    size_field?: string
    chart_type?: string
    field?: string
    limit?: number
    [key: string]: any
  }
}

// ===== Dashboard Types =====
export interface DashboardWidget {
  id: string
  type: 'summary_card' | 'chart' | 'table' | 'insight_feed'
  title: string
  data: any
  config: Record<string, any>
  position: {
    row: number
    col: number
    width: number
    height: number
  }
  last_updated?: string
}

export interface SummaryCard {
  title: string
  value: string | number
  change?: {
    value: number
    trend: 'up' | 'down' | 'stable'
    period: string
  }
  status?: 'normal' | 'warning' | 'critical'
  color?: 'primary' | 'accent' | 'warning' | 'danger'
}

// ===== Investigation Types =====
export interface Investigation {
  id: string
  title: string
  status: 'open' | 'in_progress' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  created_by: string
  created_at: string
  updated_at: string
  description?: string
  tags: string[]
  context: {
    session_id?: string
    filters?: Record<string, any>
    queries?: string[]
  }
  timeline: TimelineEntry[]
}

export interface TimelineEntry {
  id: string
  timestamp: string
  type: 'query' | 'finding' | 'note' | 'action'
  title: string
  content: string
  user: string
  metadata?: Record<string, any>
}

// ===== Report Types =====
export interface Report {
  id: string
  title: string
  type: 'executive' | 'technical' | 'compliance' | 'incident'
  format: 'pdf' | 'html' | 'json'
  status: 'generating' | 'ready' | 'failed'
  created_by: string
  created_at: string
  parameters: {
    time_range: TimeRange
    filters?: Record<string, any>
    sections: ReportSection[]
  }
  download_url?: string
  metadata?: Record<string, any>
}

export interface ReportSection {
  type: 'summary' | 'chart' | 'table' | 'findings' | 'recommendations'
  title: string
  config: Record<string, any>
  data?: any
}

// ===== Time & Filter Types =====
export interface TimeRange {
  start: string
  end: string
  label?: string
  relative?: string // "last_24h", "last_week", etc.
}

export interface Filter {
  field: string
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'gt' | 'lt' | 'in' | 'not_in'
  value: any
  label?: string
}

// ===== SIEM Connector Types =====
export interface SiemConnector {
  id: string
  type: 'elastic' | 'wazuh' | 'splunk' | 'qradar' | 'dataset'
  name: string
  status: 'connected' | 'connecting' | 'error' | 'disconnected'
  config: {
    url?: string
    version?: string
    indices?: string[]
  }
  health?: {
    last_check: string
    response_time: number
    error_count: number
  }
}

// ===== User & Auth Types =====
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'analyst' | 'viewer'
  permissions: string[]
  last_login?: string
  preferences: {
    theme: 'dark' | 'light'
    default_time_range: string
    dashboard_layout: string
    notifications: boolean
  }
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

// ===== UI State Types =====
export interface AppMode {
  current: 'landing' | 'dashboard' | 'chat' | 'hybrid' | 'reports' | 'investigations' | 'admin'
}

export interface UIState {
  mode: AppMode['current']
  sidebar_collapsed: boolean
  chat_panel_open: boolean
  loading: boolean
  error: string | null
}

// ===== API Response Types =====
export interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
  error?: string
  timestamp?: string
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

// ===== WebSocket Types =====
export interface WebSocketMessage {
  type: 'chat_response' | 'notification' | 'system_update' | 'error'
  data: any
  session_id?: string
  timestamp: string
}

// ===== Context Types =====
export interface ConversationContext {
  conversation_id: string
  history: ChatMessage[]
  entities: Record<string, any>
  filters: Filter[]
  time_range?: TimeRange
  metadata: Record<string, any>
}

// ===== Error Types =====
export interface AppError {
  code: string
  message: string
  details?: string
  timestamp: string
  context?: Record<string, any>
}

// ===== Component Props =====
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

// ===== Utility Types =====
export type DeepPartial<T> = {
  [P in keyof T]?: DeepPartial<T[P]>
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K
}[keyof T]
