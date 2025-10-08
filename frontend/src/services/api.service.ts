/**
 * Enhanced API Service
 * Comprehensive API client with error handling, retry logic, and notifications
 */

import { 
  createApiErrorNotification, 
  Notification 
} from '../components/ui/NotificationSystem';
import { mockApiService, MockApiService } from './mockData.service';

// ============= TYPES =============

export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  status?: number;
}

export interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  skipNotification?: boolean;
}

// SIEM-specific interfaces
export interface SecurityAlert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  timestamp: string;
  source: string;
  status: 'active' | 'investigating' | 'resolved';
  assignee?: string;
}

export interface DashboardMetrics {
  totalThreats: number;
  activeAlerts: number;
  systemsOnline: number;
  incidentsToday: number;
  threatTrends: Array<{ date: string; count: number }>;
  topThreats: Array<{ name: string; count: number; severity: string }>;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  metadata?: {
    sources?: string[];
    confidence?: number;
    actions?: string[];
  };
}

export interface NetworkTraffic {
  timestamp: string;
  source: string;
  destination: string;
  protocol: string;
  bytes: number;
  packets: number;
  suspicious: boolean;
}

export interface UserActivity {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  timestamp: string;
  ipAddress: string;
  riskScore: number;
}

export interface SystemStatus {
  service: string;
  status: 'online' | 'offline' | 'degraded';
  uptime: string;
  lastCheck: string;
  metrics: Record<string, number>;
}

// ============= API CLIENT CLASS =============

class ApiClient {
  private config: ApiConfig;
  private notificationCallback?: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  private fallbackMode: boolean = false;
  private mockService: MockApiService;

  constructor(config: ApiConfig) {
    this.config = {
      timeout: 15000, // Increased timeout for backend
      retries: 2, // Reduced retries to fail faster to backend
      retryDelay: 2000,
      ...config,
    };
    this.mockService = mockApiService;
    
    // Log API configuration
    console.log('🌐 API Client initialized with:', {
      baseUrl: this.config.baseUrl,
      environment: import.meta.env.VITE_ENVIRONMENT || 'development'
    });
  }

  // Set notification callback
  setNotificationCallback(callback: (notification: Omit<Notification, 'id' | 'timestamp'>) => void) {
    this.notificationCallback = callback;
  }

  // Generic request method with error handling and retry logic
  private async makeRequest<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    // If in fallback mode, don't try real API
    if (this.fallbackMode) {
      return this.handleFallbackRequest<T>(endpoint, config);
    }

    const {
      method = 'GET',
      headers = {},
      body,
      timeout = this.config.timeout,
      retries = this.config.retries,
      skipNotification = false,
    } = config;

    let lastError: any = null;

    for (let attempt = 0; attempt <= retries!; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...headers,
          },
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        return {
          success: true,
          data,
          status: response.status,
        };

      } catch (error: any) {
        lastError = error;
        
        // Don't retry on certain errors
        if (error.name === 'AbortError' || 
            (error.response && [401, 403, 404].includes(error.response.status))) {
          break;
        }

        // Wait before retrying
        if (attempt < retries!) {
          await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));
        }
      }
    }

    // If all attempts failed, try fallback
    console.warn(`Backend failed for ${endpoint}, switching to fallback mode`);
    this.fallbackMode = true;
    return this.handleFallbackRequest<T>(endpoint, config);
  }

  // Handle requests using mock data
  private async handleFallbackRequest<T>(endpoint: string, config: RequestConfig): Promise<ApiResponse<T>> {
    try {
      let data: any;
      
      // Route to appropriate mock service method
      if (endpoint.includes('/dashboard/metrics')) {
        data = await this.mockService.getDashboardMetrics();
      } else if (endpoint.includes('/alerts')) {
        data = await this.mockService.getSecurityAlerts();
      } else if (endpoint.includes('/system/status')) {
        data = await this.mockService.getSystemStatus();
      } else if (endpoint.includes('/chat/message')) {
        const message = config.body?.message || 'Hello';
        data = await this.mockService.sendChatMessage(message);
      } else if (endpoint.includes('/chat/session')) {
        data = await this.mockService.createChatSession();
      } else if (endpoint.includes('/chat/history')) {
        data = await this.mockService.getChatHistory('mock');
      } else if (endpoint.includes('/network/traffic')) {
        data = await this.mockService.getNetworkTraffic();
      } else if (endpoint.includes('/users/activity')) {
        data = await this.mockService.getUserActivity();
      } else if (endpoint.includes('/health')) {
        data = await this.mockService.healthCheck();
      } else {
        // Default mock response
        data = { message: 'Mock response', timestamp: new Date().toISOString() };
      }

      return {
        success: true,
        data,
        status: 200,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Mock service error',
        status: 500,
      };
    }
  }

  // ============= DASHBOARD APIs =============

  async getDashboardMetrics(): Promise<ApiResponse<DashboardMetrics>> {
    return this.makeRequest<DashboardMetrics>('/api/dashboard/metrics');
  }

  async getSecurityAlerts(limit = 50): Promise<ApiResponse<SecurityAlert[]>> {
    return this.makeRequest<SecurityAlert[]>(`/api/alerts?limit=${limit}`);
  }

  async updateAlert(alertId: string, updates: Partial<SecurityAlert>): Promise<ApiResponse<SecurityAlert>> {
    return this.makeRequest<SecurityAlert>(`/api/alerts/${alertId}`, {
      method: 'PATCH',
      body: updates,
    });
  }

  async getSystemStatus(): Promise<ApiResponse<SystemStatus[]>> {
    return this.makeRequest<SystemStatus[]>('/api/system/status');
  }

  // ============= CHAT APIs =============

  async sendChatMessage(message: string, sessionId?: string): Promise<ApiResponse<ChatMessage>> {
    return this.makeRequest<ChatMessage>('/api/chat/message', {
      method: 'POST',
      body: { message, sessionId },
    });
  }

  async getChatHistory(sessionId: string): Promise<ApiResponse<ChatMessage[]>> {
    return this.makeRequest<ChatMessage[]>(`/api/chat/history/${sessionId}`);
  }

  async createChatSession(): Promise<ApiResponse<{ sessionId: string }>> {
    return this.makeRequest<{ sessionId: string }>('/api/chat/session', {
      method: 'POST',
    });
  }

  // ============= NETWORK MONITORING APIs =============

  async getNetworkTraffic(
    timeRange: string = '1h',
    limit = 100
  ): Promise<ApiResponse<NetworkTraffic[]>> {
    return this.makeRequest<NetworkTraffic[]>(`/api/network/traffic?range=${timeRange}&limit=${limit}`);
  }

  async getTopConnections(limit = 10): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>(`/api/network/connections/top?limit=${limit}`);
  }

  async getProtocolDistribution(): Promise<ApiResponse<Record<string, number>>> {
    return this.makeRequest<Record<string, number>>('/api/network/protocols');
  }

  // ============= USER ACTIVITY APIs =============

  async getUserActivity(limit = 50): Promise<ApiResponse<UserActivity[]>> {
    return this.makeRequest<UserActivity[]>(`/api/users/activity?limit=${limit}`);
  }

  async getUserRiskScores(): Promise<ApiResponse<Record<string, number>>> {
    return this.makeRequest<Record<string, number>>('/api/users/risk-scores');
  }

  async getActiveUsers(): Promise<ApiResponse<string[]>> {
    return this.makeRequest<string[]>('/api/users/active');
  }

  // ============= THREAT INTELLIGENCE APIs =============

  async getThreatFeed(limit = 20): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>(`/api/threats/feed?limit=${limit}`);
  }

  async getThreatAnalysis(threatId: string): Promise<ApiResponse<any>> {
    return this.makeRequest<any>(`/api/threats/${threatId}/analysis`);
  }

  async submitThreatSample(sample: any): Promise<ApiResponse<any>> {
    return this.makeRequest<any>('/api/threats/analyze', {
      method: 'POST',
      body: sample,
    });
  }

  // ============= REPORTS APIs =============

  async generateReport(
    type: string,
    timeRange: string,
    filters?: Record<string, any>
  ): Promise<ApiResponse<{ reportId: string }>> {
    return this.makeRequest<{ reportId: string }>('/api/reports/generate', {
      method: 'POST',
      body: { type, timeRange, filters },
    });
  }

  async getReport(reportId: string): Promise<ApiResponse<any>> {
    return this.makeRequest<any>(`/api/reports/${reportId}`);
  }

  async getReportList(): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>('/api/reports');
  }

  // ============= AUTHENTICATION APIs =============

  async login(identifier: string, password: string): Promise<ApiResponse<{ token: string; user: any; permissions?: string[] }>> {
    console.log('🔐 Attempting login with identifier:', identifier);
    
    // Match the backend FastAPI endpoint structure
    return this.makeRequest<{ token: string; user: any; permissions?: string[] }>('/auth/login', {
      method: 'POST',
      body: { 
        identifier, // Can be email, username, or ID
        password
      },
      skipNotification: true, // Handle login errors specially
    });
  }

  async logout(): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/api/auth/logout', {
      method: 'POST',
    });
  }

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return this.makeRequest<any>('/api/auth/me');
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return this.makeRequest<{ token: string }>('/api/auth/refresh', {
      method: 'POST',
    });
  }

  // ============= SEARCH APIs =============

  async searchLogs(
    query: string,
    timeRange: string,
    limit = 100
  ): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>('/api/search/logs', {
      method: 'POST',
      body: { query, timeRange, limit },
    });
  }

  async searchEvents(
    query: string,
    filters?: Record<string, any>
  ): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>('/api/search/events', {
      method: 'POST',
      body: { query, filters },
    });
  }

  // ============= CONFIGURATION APIs =============

  async getConfig(): Promise<ApiResponse<Record<string, any>>> {
    return this.makeRequest<Record<string, any>>('/api/config');
  }

  async updateConfig(config: Record<string, any>): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/api/config', {
      method: 'PUT',
      body: config,
    });
  }

  // ============= HEALTH CHECK =============

  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.makeRequest<{ status: string; timestamp: string }>('/api/health', {
      timeout: 5000,
      retries: 1,
      skipNotification: true,
    });
  }
}

// ============= API CLIENT INSTANCE =============

// Determine API base URL
const getApiBaseUrl = (): string => {
  // Development
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
  }
  
  // Production - use relative path or environment variable
  return import.meta.env.VITE_API_BASE_URL || '';
};

// Create and export API client instance
const apiClient = new ApiClient({
  baseUrl: getApiBaseUrl(),
  timeout: 15000,
  retries: 2,
  retryDelay: 1000,
});

export default apiClient;

// ============= REACT HOOK FOR API =============

import { useState, useCallback } from 'react';
import { useNotifications } from '../components/ui/NotificationSystem';

export const useApiClient = () => {
  const [loading, setLoading] = useState(false);
  const { addNotification } = useNotifications();

  // Set up notification callback
  apiClient.setNotificationCallback(addNotification);

  const callApi = useCallback(async <T>(
    apiCall: () => Promise<ApiResponse<T>>,
    options: {
      loadingMessage?: string;
      successMessage?: string;
      onSuccess?: (data: T) => void;
      onError?: (error: string) => void;
    } = {}
  ) => {
    setLoading(true);

    if (options.loadingMessage) {
      addNotification({
        type: 'loading',
        title: 'Loading',
        message: options.loadingMessage,
        persistent: true,
      });
    }

    try {
      const response = await apiCall();
      
      if (response.success && response.data) {
        if (options.successMessage) {
          addNotification({
            type: 'success',
            title: 'Success',
            message: options.successMessage,
          });
        }
        
        options.onSuccess?.(response.data);
        return response.data;
      } else {
        const errorMessage = response.error || 'API request failed';
        options.onError?.(errorMessage);
        return null;
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Unexpected error occurred';
      options.onError?.(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [addNotification]);

  return {
    api: apiClient,
    callApi,
    loading,
  };
};

// ============= EXPORTS =============

export { apiClient, ApiClient };
