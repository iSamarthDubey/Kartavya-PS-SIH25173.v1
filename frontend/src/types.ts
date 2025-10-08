// Shared types for the frontend application

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: string;
  queryInfo?: {
    originalQuery: string;
    parsedIntent: string;
    generatedQuery: string;
    executionTime: number;
  };
}

export interface SystemStatus {
  status: 'online' | 'offline' | 'degraded';
  lastUpdate: Date;
  metrics: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
  };
}

export interface ThreatAlert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  timestamp: Date;
  source: string;
  status: 'open' | 'investigating' | 'resolved';
}

export interface DashboardMetrics {
  activeAlerts: number;
  systemHealth: number;
  threatsBlocked: number;
  totalEvents: number;
  recentAlerts: ThreatAlert[];
}

export interface Report {
  id: string;
  title: string;
  type: 'security_summary' | 'threat_analysis' | 'incident_report' | 'compliance_audit';
  status: 'generating' | 'completed' | 'failed';
  createdAt: Date;
  completedAt?: Date;
  description: string;
  size?: string;
}

export interface User {
  id: string;
  username: string;
  role: 'admin' | 'analyst' | 'viewer';
  lastLogin: Date;
  isActive: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatResponse extends ApiResponse {
  data?: {
    response: string;
    context?: string;
    queryInfo?: {
      originalQuery: string;
      parsedIntent: string;
      generatedQuery: string;
      executionTime: number;
    };
  };
}
