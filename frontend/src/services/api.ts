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
  PaginatedResponse
} from '@/types'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('synrgy_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    // Handle common error scenarios
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('synrgy_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// ===== Authentication APIs =====
export const authApi = {
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', {
      identifier: credentials.email, // Backend expects 'identifier' not 'email'
      password: credentials.password
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
  }
}

// ===== Chat & Assistant APIs =====
export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/assistant/chat', request)
    return response.data
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
    const response = await api.get<ApiResponse<{
      conversation_id: string
      history: any[]
      total_messages: number
    }>>(`/assistant/history/${conversationId}?limit=${limit}`)
    return response.data
  },

  clearHistory: async (conversationId: string) => {
    const response = await api.delete<ApiResponse>(`/assistant/history/${conversationId}`)
    return response.data
  },

  getSuggestions: async () => {
    const response = await api.get<ApiResponse<{
      suggestions: Array<{
        category: string
        queries: string[]
      }>
    }>>('/assistant/suggestions')
    return response.data
  }
}

// ===== Dashboard APIs =====
export const dashboardApi = {
  getOverview: async () => {
    const response = await api.get<ApiResponse<{
      summary_cards: Array<{
        title: string
        value: string | number
        change?: { value: number; trend: 'up' | 'down' | 'stable' }
        status?: 'normal' | 'warning' | 'critical'
      }>
      recent_alerts: any[]
      system_health: any
    }>>('/dashboard')
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
  }
}

// ===== Query APIs =====
export const queryApi = {
  execute: async (data: {
    dsl: Record<string, any>
    size?: number
    execute?: boolean
  }) => {
    const response = await api.post<ApiResponse<{
      hits: any
      aggregations?: any
      took: number
      warnings?: string[]
    }>>('/query/run', data)
    return response.data
  },

  validate: async (dsl: Record<string, any>) => {
    const response = await api.post<ApiResponse<{
      valid: boolean
      errors?: string[]
      warnings?: string[]
    }>>('/query/validate', { dsl })
    return response.data
  },

  suggest: async (partialQuery: string) => {
    const response = await api.post<ApiResponse<string[]>>('/query/suggest', { 
      text: partialQuery 
    })
    return response.data
  }
}

// ===== Reports APIs =====
export const reportsApi = {
  list: async (page: number = 1, limit: number = 20) => {
    const response = await api.get<PaginatedResponse<Report>>(`/reports?page=${page}&limit=${limit}`)
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
    const response = await api.post<ApiResponse<{ report_id: string; status: string }>>('/reports/generate', data)
    return response.data
  },

  download: async (reportId: string) => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob'
    })
    return response
  },

  delete: async (reportId: string) => {
    const response = await api.delete<ApiResponse>(`/reports/${reportId}`)
    return response.data
  }
}

// ===== Investigations APIs =====
export const investigationsApi = {
  list: async (page: number = 1, limit: number = 20, status?: string) => {
    const params = new URLSearchParams({ 
      page: page.toString(), 
      limit: limit.toString() 
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
    const response = await api.put<ApiResponse<Investigation>>(`/investigations/${investigationId}`, data)
    return response.data
  },

  delete: async (investigationId: string) => {
    const response = await api.delete<ApiResponse>(`/investigations/${investigationId}`)
    return response.data
  }
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
    const response = await api.post<ApiResponse<{
      status: 'success' | 'error'
      message: string
      details?: any
    }>>(`/admin/connectors/${connectorId}/test`)
    return response.data
  },

  deleteConnector: async (connectorId: string) => {
    const response = await api.delete<ApiResponse>(`/admin/connectors/${connectorId}`)
    return response.data
  },

  getAuditLogs: async (page: number = 1, limit: number = 50) => {
    const response = await api.get<PaginatedResponse<any>>(`/admin/audit?page=${page}&limit=${limit}`)
    return response.data
  },

  getUsage: async () => {
    const response = await api.get<ApiResponse<{
      query_counts: Record<string, number>
      user_activity: any[]
      system_metrics: any
    }>>('/admin/usage')
    return response.data
  }
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
      baseURL: import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'
    })
    return response.data
  },

  ping: async () => {
    // Ping endpoint is also at root level
    const response = await axios.get<{ status: string; timestamp: string }>('/ping', {
      baseURL: import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'
    })
    return response.data
  }
}

// Export the base axios instance for custom requests
export { api }

// Default export with all API groups
export default {
  auth: authApi,
  chat: chatApi,
  dashboard: dashboardApi,
  query: queryApi,
  reports: reportsApi,
  investigations: investigationsApi,
  admin: adminApi,
  system: systemApi
}
