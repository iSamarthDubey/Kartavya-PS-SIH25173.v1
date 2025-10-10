/**
 * KARTAVYA SIEM - API Service
 * Handles all backend communication for the Conversational Assistant
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AdvancedSecurityEntity } from './advancedEntityRecognition';

// Types matching backend models
export interface ChatRequest {
  query: string;
  conversation_id?: string;
  user_context?: Record<string, any>;
  filters?: Record<string, any>;
  limit?: number;
}

export interface ChatResponse {
  conversation_id: string;
  query: string;
  intent: string;
  confidence: number;
  entities: AdvancedSecurityEntity[]; // 🚀 Enhanced to support advanced entities
  siem_query: Record<string, any>;
  results: Array<Record<string, any>>;
  summary: string;
  visualizations?: Array<Record<string, any>>;
  suggestions?: string[];
  // 🆕 Advanced metadata for threat intelligence
  metadata: {
    query_time?: number;
    sources?: string[];
    risk_score?: number;
    kql?: string;
    entity_count?: number;
    high_risk_entities?: number;
    timestamp?: string;
    [key: string]: any;
  };
  status: 'success' | 'error' | 'blocked' | 'clarification_needed';
  error?: string;
  // 🆕 Advanced action suggestions based on detected entities
  entity_actions?: Array<{
    label: string;
    action: string;
    entities: AdvancedSecurityEntity[];
    icon: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
  }>;
}

export interface HealthCheck {
  status: string;
  timestamp: string;
  services: {
    pipeline: boolean;
    siem_connector: boolean;
    context_manager: boolean;
    schema_mapper: boolean;
  };
  health_score: 'excellent' | 'good' | 'degraded' | 'critical';
}

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Use environment variable or fallback to localhost
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds for SIEM queries
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth and logging
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params
        });
        
        return config;
      },
      (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status}`, {
          url: response.config.url,
          data: response.data
        });
        return response;
      },
      (error) => {
        console.error('❌ API Response Error:', {
          status: error.response?.status,
          message: error.response?.data?.message || error.message,
          url: error.config?.url
        });

        // Handle specific error cases
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    try {
      const response: AxiosResponse<HealthCheck> = await this.api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      // Return degraded status if health check fails
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        services: {
          pipeline: false,
          siem_connector: false,
          context_manager: false,
          schema_mapper: false
        },
        health_score: 'critical'
      };
    }
  }

  // Main chat endpoint
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response: AxiosResponse<ChatResponse> = await this.api.post('/api/assistant/chat', request);
      return response.data;
    } catch (error: any) {
      console.error('Chat request failed:', error);
      
      // Handle network errors gracefully
      if (!error.response) {
        return {
          conversation_id: request.conversation_id || 'error',
          query: request.query,
          intent: 'error',
          confidence: 0,
          entities: [],
          siem_query: {},
          results: [],
          summary: 'Unable to connect to the SIEM Assistant backend. Please check your connection and try again.',
          metadata: { timestamp: new Date().toISOString(), error: 'Network error' },
          status: 'error',
          error: 'Network connection failed'
        };
      }

      // Return backend error response if available
      if (error.response.data && typeof error.response.data === 'object') {
        return error.response.data;
      }

      // Fallback error response
      return {
        conversation_id: request.conversation_id || 'error',
        query: request.query,
        intent: 'error',
        confidence: 0,
        entities: [],
        siem_query: {},
        results: [],
        summary: `An error occurred: ${error.message}`,
        metadata: { timestamp: new Date().toISOString() },
        status: 'error',
        error: error.message
      };
    }
  }

  // Get conversation history
  async getHistory(conversationId: string, limit: number = 10) {
    try {
      const response = await this.api.get(`/api/assistant/history/${conversationId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get conversation history:', error);
      throw error;
    }
  }

  // Clear conversation history
  async clearHistory(conversationId: string) {
    try {
      const response = await this.api.delete(`/api/assistant/history/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to clear conversation history:', error);
      throw error;
    }
  }

  // Get query suggestions
  async getQuerySuggestions() {
    try {
      const response = await this.api.get('/api/assistant/suggestions');
      return response.data;
    } catch (error) {
      console.error('Failed to get query suggestions:', error);
      // Return fallback suggestions
      return [
        {
          category: 'Authentication',
          queries: [
            'Show me failed login attempts in the last hour',
            'Which users had the most authentication failures today?',
            'Are there any brute force attempts detected?'
          ]
        },
        {
          category: 'Threats',
          queries: [
            'Any malware detected in the last 24 hours?',
            'Show critical security alerts from today',
            'What are the top threat indicators?'
          ]
        }
      ];
    }
  }

  // 🚀 ADVANCED ENTITY PROCESSING ENDPOINTS
  
  // Extract advanced entities from text
  async extractAdvancedEntities(text: string): Promise<AdvancedSecurityEntity[]> {
    try {
      const response = await this.api.post('/api/entities/extract', { text });
      return response.data.entities || [];
    } catch (error) {
      console.error('Failed to extract advanced entities:', error);
      // Return empty array if backend is unavailable
      return [];
    }
  }
  
  // Get threat intelligence for multiple entities
  async bulkThreatIntelligence(entities: AdvancedSecurityEntity[]): Promise<AdvancedSecurityEntity[]> {
    try {
      const response = await this.api.post('/api/entities/enrich', { entities });
      return response.data.enriched_entities || entities;
    } catch (error) {
      console.error('Failed to get bulk threat intelligence:', error);
      return entities; // Return original entities if enrichment fails
    }
  }
  
  // Generate smart actions based on entities
  async generateEntityActions(entities: AdvancedSecurityEntity[]) {
    try {
      const response = await this.api.post('/api/entities/actions', { entities });
      return response.data.actions || [];
    } catch (error) {
      console.error('Failed to generate entity actions:', error);
      // Return empty array if backend is unavailable
      return [];
    }
  }
  
  // Advanced threat hunting endpoint
  async threatHunt(params: {
    entities?: AdvancedSecurityEntity[];
    techniques?: string[];
    time_range?: string;
    severity?: 'low' | 'medium' | 'high' | 'critical';
  }) {
    try {
      const response = await this.api.post('/api/hunt/threats', params);
      return response.data;
    } catch (error) {
      console.error('Failed to execute threat hunt:', error);
      throw error;
    }
  }
  
  // MITRE ATT&CK kill chain analysis
  async analyzeMITREChain(techniques: string[]) {
    try {
      const response = await this.api.post('/api/mitre/analyze', { techniques });
      return response.data;
    } catch (error) {
      console.error('Failed to analyze MITRE chain:', error);
      throw error;
    }
  }
  
  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      await this.api.get('/ping');
      return true;
    } catch (error) {
      return false;
    }
  }

  // Get backend status
  async getStatus() {
    try {
      const response = await this.api.get('/');
      return response.data;
    } catch (error) {
      console.error('Failed to get backend status:', error);
      return null;
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
