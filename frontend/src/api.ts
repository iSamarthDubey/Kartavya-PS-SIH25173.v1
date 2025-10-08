import { ChatResponse, DashboardMetrics, Report, SystemStatus, User } from './types';

const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  // Chat API
  async sendChatMessage(
    query: string,
    sessionId?: string
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/v1/chat/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        session_id: sessionId,
      }),
    });
  }

  async getChatHistory(sessionId: string) {
    return this.request(`/api/v1/chat/history/${sessionId}`);
  }

  async clearChatHistory(sessionId: string) {
    return this.request(`/api/v1/chat/history/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // Dashboard API
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return this.request<DashboardMetrics>('/api/v1/dashboard/metrics');
  }

  async getSystemStatus(): Promise<SystemStatus> {
    return this.request<SystemStatus>('/api/v1/system/status');
  }

  // Reports API
  async getReports(): Promise<Report[]> {
    return this.request<Report[]>('/api/v1/reports');
  }

  async generateReport(type: string, config: any): Promise<Report> {
    return this.request<Report>('/api/v1/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ type, config }),
    });
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/reports/${reportId}/download`);
    if (!response.ok) {
      throw new Error(`Failed to download report: ${response.status}`);
    }
    return response.blob();
  }

  // Admin API
  async getUsers(): Promise<User[]> {
    return this.request<User[]>('/api/v1/admin/users');
  }

  async updateUser(userId: string, updates: Partial<User>): Promise<User> {
    return this.request<User>(`/api/v1/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Mock data generators for demo mode
export const mockData = {
  generateDashboardMetrics: (): DashboardMetrics => ({
    activeAlerts: Math.floor(Math.random() * 20) + 5,
    systemHealth: Math.floor(Math.random() * 20) + 80,
    threatsBlocked: Math.floor(Math.random() * 1000) + 500,
    totalEvents: Math.floor(Math.random() * 10000) + 5000,
    recentAlerts: [
      {
        id: '1',
        severity: 'critical' as const,
        title: 'Suspicious Login Detected',
        description: 'Multiple failed login attempts from unknown IP',
        timestamp: new Date(Date.now() - 1000 * 60 * 15),
        source: 'Authentication System',
        status: 'investigating' as const,
      },
      {
        id: '2',
        severity: 'high' as const,
        title: 'Malware Signature Match',
        description: 'Known malware hash detected in file system',
        timestamp: new Date(Date.now() - 1000 * 60 * 30),
        source: 'Endpoint Protection',
        status: 'open' as const,
      },
      {
        id: '3',
        severity: 'medium' as const,
        title: 'Unusual Network Traffic',
        description: 'High volume of outbound connections detected',
        timestamp: new Date(Date.now() - 1000 * 60 * 45),
        source: 'Network Monitor',
        status: 'resolved' as const,
      },
    ],
  }),

  generateSystemStatus: (): SystemStatus => ({
    status: 'online' as const,
    lastUpdate: new Date(),
    metrics: {
      cpu: Math.floor(Math.random() * 40) + 30,
      memory: Math.floor(Math.random() * 30) + 50,
      disk: Math.floor(Math.random() * 20) + 40,
      network: Math.floor(Math.random() * 25) + 25,
    },
  }),

  generateChatResponse: (query: string): ChatResponse => ({
    success: true,
    data: {
      response: `I understand you're asking about "${query}". Here's what I found in the security logs: Based on my analysis, there are several relevant events that match your criteria. The system has processed ${Math.floor(Math.random() * 1000) + 100} related events in the last 24 hours.`,
      context: 'security_analysis',
      queryInfo: {
        originalQuery: query,
        parsedIntent: 'threat_investigation',
        generatedQuery: `GET /api/v1/events?q=${encodeURIComponent(query)}&time_range=24h`,
        executionTime: Math.floor(Math.random() * 500) + 100,
      },
    },
  }),

  generateReports: (): Report[] => [
    {
      id: '1',
      title: 'Daily Security Summary',
      type: 'security_summary',
      status: 'completed',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
      completedAt: new Date(Date.now() - 1000 * 60 * 60),
      description: 'Comprehensive overview of security events from the last 24 hours',
      size: '2.3 MB',
    },
    {
      id: '2',
      title: 'Weekly Threat Analysis',
      type: 'threat_analysis',
      status: 'generating',
      createdAt: new Date(Date.now() - 1000 * 60 * 30),
      description: 'Detailed analysis of threat patterns and trends',
    },
    {
      id: '3',
      title: 'Incident Response Report',
      type: 'incident_report',
      status: 'completed',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
      completedAt: new Date(Date.now() - 1000 * 60 * 60 * 23),
      description: 'Analysis of recent security incidents and response actions',
      size: '1.8 MB',
    },
  ],
};
