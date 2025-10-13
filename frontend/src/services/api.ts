/**
 * API Client Service for SYNRGY Frontend
 * Handles all HTTP communication with the FastAPI backend
 */

import axios, { AxiosResponse } from 'axios'
import type {
  ChatRequest,
  ChatResponse,
  ApiResponse,
  Investigation,
  Report,
  SiemConnector,
  DashboardWidget,
  User,
  PaginatedResponse,
} from '@/types'

// Enhanced retry configuration
const MAX_RETRIES = parseInt(import.meta.env.VITE_MAX_RETRY_ATTEMPTS || '3')
const RETRY_DELAY = parseInt(import.meta.env.VITE_RETRY_DELAY || '1000')
const REQUEST_TIMEOUT = parseInt(import.meta.env.VITE_REQUEST_TIMEOUT || '30000')

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Exponential backoff retry helper
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

const isRetryableError = (error: any): boolean => {
  if (!error.response) {
    // Network errors (no response)
    return true
  }

  const status = error.response.status
  // Retry on 5xx server errors and 429 rate limiting
  return status >= 500 || status === 429
}

const retryRequest = async (
  requestFn: () => Promise<any>,
  maxRetries: number = MAX_RETRIES
): Promise<any> => {
  let lastError: any

  for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
    try {
      return await requestFn()
    } catch (error: any) {
      lastError = error

      if (attempt > maxRetries || !isRetryableError(error)) {
        throw error
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = RETRY_DELAY * Math.pow(2, attempt - 1)
      if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
        console.log(
          `Request failed (attempt ${attempt}/${maxRetries + 1}), retrying in ${delay}ms...`
        )
      }
      await sleep(delay)
    }
  }

  throw lastError
}

// Request interceptor for adding auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('synrgy_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for comprehensive error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  error => {
    // Handle common error scenarios
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('synrgy_token')
      if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
        console.warn('Authentication expired, redirecting to login')
      }
      window.location.href = '/login'
      return Promise.reject(new Error('Authentication expired'))
    }

    if (error.response?.status === 403) {
      return Promise.reject(new Error('Access forbidden'))
    }

    if (error.response?.status === 429) {
      // Let the retry logic handle this
      return Promise.reject(error)
    }

    if (error.response?.status >= 500) {
      // Let the retry logic handle this
      return Promise.reject(error)
    }

    if (!error.response) {
      return Promise.reject(new Error('Network error - please check your connection'))
    }

    // For other errors, include response data if available
    const errorMessage =
      error.response?.data?.message || error.response?.data?.detail || error.message
    return Promise.reject(new Error(errorMessage))
  }
)

// ===== Authentication APIs =====

// Fixed interface to match backend expectations
interface LoginCredentials {
  identifier: string // Changed from 'email' to match backend
  password: string
}

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await api.post('/auth/login', {
      identifier: credentials.identifier, // Now consistent with interface
      password: credentials.password,
    })
    return response.data
  },

  logout: async () => {
    const response = await api.post<ApiResponse>('/auth/logout')
    return response.data
  },

  me: async () => {
    const response = await api.get('/auth/profile')
    return response.data
  },

  refreshToken: async () => {
    const response = await api.post<ApiResponse<{ token: string }>>('/auth/refresh')
    return response.data
  },
}

// ===== Chat & Assistant APIs =====
export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    return await retryRequest(async () => {
      try {
        // Try the standard assistant endpoint first with retry logic
        const response = await api.post<ChatResponse>('/assistant/chat', request)
        return response.data
      } catch (error: any) {
        // If standard endpoint fails, try Windows-specific endpoint as fallback
        if (error.response?.status === 400 || error.response?.status === 503) {
          const windowsResponse = await windowsApi.simpleChat(request.query)
          // Convert Windows response to standard ChatResponse format
          return {
            conversation_id: 'fallback',
            query: request.query,
            intent: windowsResponse.intent,
            confidence: windowsResponse.confidence,
            entities: windowsResponse.entities || [],
            siem_query: windowsResponse.siem_query,
            results: windowsResponse.results,
            summary: windowsResponse.summary,
            visualizations: windowsResponse.visualizations || [],
            suggestions: windowsResponse.suggestions || [],
            metadata: windowsResponse.metadata,
            status: windowsResponse.status,
            error: windowsResponse.error,
          }
        }
        throw error
      }
    })
  },

  clarify: async (data: {
    conversation_id: string
    original_query: string
    clarification_choice: string
  }) => {
    const response = await api.post<ApiResponse>('/assistant/clarify', data)
    return response.data
  },

  getHistory: async (conversationId: string, limit: number = 10) => {
    const response = await api.get<
      ApiResponse<{
        conversation_id: string
        history: any[]
        total_messages: number
      }>
    >(`/assistant/history/${conversationId}?limit=${limit}`)
    return response.data
  },

  clearHistory: async (conversationId: string) => {
    const response = await api.delete<ApiResponse>(`/assistant/history/${conversationId}`)
    return response.data
  },

  getSuggestions: async () => {
    const response = await api.get<
      ApiResponse<{
        suggestions: Array<{
          category: string
          queries: string[]
        }>
      }>
    >('/assistant/suggestions')
    return response.data
  },
}

// ===== Dashboard APIs =====
export const dashboardApi = {
  getOverview: async () => {
    // Use our new Windows data endpoint instead of static data
    const response = await api.get<
      ApiResponse<{
        summary_cards: Array<{
          title: string
          value: string | number
          change?: { value: number; trend: 'up' | 'down' | 'stable' }
          status?: 'normal' | 'warning' | 'critical'
        }>
        recent_alerts: any[]
        system_health: any
      }>
    >('/windows/dashboard-summary')
    return response.data
  },

  getWidgets: async () => {
    const response = await api.get<ApiResponse<DashboardWidget[]>>('/dashboard/widgets')
    return response.data
  },

  saveWidget: async (widget: Partial<DashboardWidget>) => {
    const response = await api.post<ApiResponse<DashboardWidget>>('/dashboard/widgets', widget)
    return response.data
  },

  deleteWidget: async (widgetId: string) => {
    const response = await api.delete<ApiResponse>(`/dashboard/widgets/${widgetId}`)
    return response.data
  },
}

// ===== Query APIs =====
export const queryApi = {
  // Execute natural language query
  execute: async (data: {
    query: string
    params?: Record<string, any>
    context?: Record<string, any>
  }) => {
    const response = await api.post<{
      success: boolean
      data?: {
        query: string
        intent: string
        entities: any[]
        summary: string
        results: any[]
        visualizations: any[]
        suggestions: string[]
        total_count: number
        query_performance: {
          execution_time_ms: number
          data_sources: string[]
        }
      }
      error?: string
      metadata?: any
    }>('/query/execute', data)
    return response.data
  },

  // Translate natural language to SIEM query
  translate: async (data: { query: string; params?: Record<string, any> }) => {
    const response = await api.post<{
      success: boolean
      data?: {
        original_query: string
        intent: string
        entities: any[]
        siem_query: any
        confidence: number
      }
      error?: string
    }>('/query/translate', data)
    return response.data
  },

  // Get query suggestions
  getSuggestions: async () => {
    const response = await api.get<{
      success: boolean
      data?: {
        security_events: string[]
        user_activity: string[]
        network_analysis: string[]
        system_monitoring: string[]
      }
      error?: string
    }>('/query/suggestions')
    return response.data
  },

  // Optimize query for better performance
  optimize: async (data: { query: string; params?: Record<string, any> }) => {
    const response = await api.post<{
      success: boolean
      data?: {
        original_query: string
        optimized_query: string
        suggestions: string[]
        performance_tips: string[]
        estimated_improvement: string
      }
      error?: string
    }>('/query/optimize', data)
    return response.data
  },
}

// ===== Windows Data APIs =====
export const windowsApi = {
  getDashboardSummary: async () => {
    const response = await api.get<{
      success: boolean
      data: {
        summary_cards: Array<{
          title: string
          value: string | number
          change: { value: number; trend: 'up' | 'down' | 'stable'; period: string }
          status: 'normal' | 'warning' | 'critical'
          color: string
        }>
        system_health: {
          health_score: string
          services: Record<string, boolean>
        }
      }
    }>('/windows/dashboard-summary')
    return response.data
  },

  getRecentEvents: async (limit: number = 10) => {
    const response = await api.get<{
      success: boolean
      data: {
        events: Array<{
          timestamp: string
          event_id: string
          message: string
          host: string
          source: any
        }>
        total: number
      }
    }>(`/windows/recent-events?limit=${limit}`)
    return response.data
  },

  getSystemMetrics: async (timeRange: string = '1h') => {
    const response = await api.get<{
      success: boolean
      data: {
        metrics: Array<{
          timestamp: string
          cpu_percent: number
          memory_percent: number
          host: string
        }>
        total: number
      }
    }>(`/windows/system-metrics?time_range=${timeRange}`)
    return response.data
  },

  simpleChat: async (query: string) => {
    const response = await api.post<{
      conversation_id: string
      query: string
      intent: string
      confidence: number
      entities: any[]
      siem_query: any
      results: any
      summary: string
      visualizations: any[]
      suggestions: string[]
      metadata: any
      status: string
      error?: string
    }>('/windows/simple-chat', { query })
    return response.data
  },
}

// ===== Reports APIs =====
export const reportsApi = {
  list: async (page: number = 1, limit: number = 20) => {
    const response = await api.get<PaginatedResponse<Report>>(
      `/reports?page=${page}&limit=${limit}`
    )
    return response.data
  },

  get: async (reportId: string) => {
    const response = await api.get<ApiResponse<Report>>(`/reports/${reportId}`)
    return response.data
  },

  generate: async (data: {
    title: string
    type: 'executive' | 'technical' | 'compliance' | 'incident'
    items: string[] // message_ids or dsl queries
    template?: string
    time_range?: { start: string; end: string }
  }) => {
    const response = await api.post<ApiResponse<{ report_id: string; status: string }>>(
      '/reports/generate',
      data
    )
    return response.data
  },

  download: async (reportId: string) => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob',
    })
    return response
  },

  delete: async (reportId: string) => {
    const response = await api.delete<ApiResponse>(`/reports/${reportId}`)
    return response.data
  },
}

// ===== Investigations APIs =====
export const investigationsApi = {
  list: async (page: number = 1, limit: number = 20, status?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    })
    if (status) params.append('status', status)

    const response = await api.get<PaginatedResponse<Investigation>>(`/investigations?${params}`)
    return response.data
  },

  get: async (investigationId: string) => {
    const response = await api.get<ApiResponse<Investigation>>(`/investigations/${investigationId}`)
    return response.data
  },

  create: async (data: Partial<Investigation>) => {
    const response = await api.post<ApiResponse<Investigation>>('/investigations', data)
    return response.data
  },

  update: async (investigationId: string, data: Partial<Investigation>) => {
    const response = await api.put<ApiResponse<Investigation>>(
      `/investigations/${investigationId}`,
      data
    )
    return response.data
  },

  delete: async (investigationId: string) => {
    const response = await api.delete<ApiResponse>(`/investigations/${investigationId}`)
    return response.data
  },
}

// ===== Platform Events APIs =====
export const platformEventsApi = {
  getCapabilities: async () => {
    const response = await api.get<{
      success: boolean
      capabilities: Record<string, any>
      timestamp: string
    }>('/events/capabilities')
    return response.data
  },

  getAuthenticationEvents: async (data: {
    query?: string
    time_range?: string
    limit?: number
  }) => {
    const response = await api.post<{
      success: boolean
      intent: string
      query_info: Record<string, any>
      platform_info: Record<string, any>
      results: Record<string, any>
      total_hits: number
      has_more: boolean
      error?: string
    }>('/events/authentication', {
      query: data.query || '',
      time_range: data.time_range || '1h',
      limit: data.limit || 100,
    })
    return response.data
  },

  getFailedLogins: async (data: { query?: string; time_range?: string; limit?: number }) => {
    const response = await api.post<{
      success: boolean
      intent: string
      query_info: Record<string, any>
      platform_info: Record<string, any>
      results: Record<string, any>
      total_hits: number
      has_more: boolean
      error?: string
    }>('/events/failed-logins', {
      query: data.query || '',
      time_range: data.time_range || '1h',
      limit: data.limit || 100,
    })
    return response.data
  },

  getSuccessfulLogins: async (data: { query?: string; time_range?: string; limit?: number }) => {
    const response = await api.post<{
      success: boolean
      intent: string
      query_info: Record<string, any>
      platform_info: Record<string, any>
      results: Record<string, any>
      total_hits: number
      has_more: boolean
      error?: string
    }>('/events/successful-logins', {
      query: data.query || '',
      time_range: data.time_range || '1h',
      limit: data.limit || 100,
    })
    return response.data
  },

  getSystemMetrics: async (data: { query?: string; time_range?: string; limit?: number }) => {
    const response = await api.post<{
      success: boolean
      intent: string
      query_info: Record<string, any>
      platform_info: Record<string, any>
      results: Record<string, any>
      total_hits: number
      has_more: boolean
      error?: string
    }>('/events/system-metrics', {
      query: data.query || '',
      time_range: data.time_range || '1h',
      limit: data.limit || 100,
    })
    return response.data
  },

  getNetworkActivity: async (data: { query?: string; time_range?: string; limit?: number }) => {
    const response = await api.post<{
      success: boolean
      intent: string
      query_info: Record<string, any>
      platform_info: Record<string, any>
      results: Record<string, any>
      total_hits: number
      has_more: boolean
      error?: string
    }>('/events/network-activity', {
      query: data.query || '',
      time_range: data.time_range || '1h',
      limit: data.limit || 100,
    })
    return response.data
  },
}

// ===== Admin APIs =====
export const adminApi = {
  getConnectors: async () => {
    const response = await api.get<ApiResponse<SiemConnector[]>>('/admin/connectors')
    return response.data
  },

  addConnector: async (connector: Partial<SiemConnector>) => {
    const response = await api.post<ApiResponse<SiemConnector>>('/admin/connectors', connector)
    return response.data
  },

  testConnector: async (connectorId: string) => {
    const response = await api.post<
      ApiResponse<{
        status: 'success' | 'error'
        message: string
        details?: any
      }>
    >(`/admin/connectors/${connectorId}/test`)
    return response.data
  },

  deleteConnector: async (connectorId: string) => {
    const response = await api.delete<ApiResponse>(`/admin/connectors/${connectorId}`)
    return response.data
  },

  getAuditLogs: async (page: number = 1, limit: number = 50) => {
    const response = await api.get<PaginatedResponse<any>>(
      `/admin/audit?page=${page}&limit=${limit}`
    )
    return response.data
  },

  getUsage: async () => {
    const response = await api.get<
      ApiResponse<{
        query_counts: Record<string, number>
        user_activity: any[]
        system_metrics: any
      }>
    >('/admin/usage')
    return response.data
  },
}

// ===== Health & System APIs =====
export const systemApi = {
  health: async () => {
    // Health endpoint is at root level, not under /api prefix
    const response = await axios.get<{
      status: string
      timestamp: string
      services: Record<string, boolean>
      health_score: string
    }>('/health', {
      baseURL: import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000',
    })
    return response.data
  },

  ping: async () => {
    // Ping endpoint is also at root level
    const response = await axios.get<{ status: string; timestamp: string }>('/ping', {
      baseURL: import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000',
    })
    return response.data
  },
}

// Export the base axios instance for custom requests
export { api }

// Default export with all API groups
export default {
  auth: authApi,
  chat: chatApi,
  dashboard: dashboardApi,
  windows: windowsApi,
  query: queryApi,
  platformEvents: platformEventsApi,
  reports: reportsApi,
  investigations: investigationsApi,
  admin: adminApi,
  system: systemApi,
}
