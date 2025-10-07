// API Service for Kartavya SIEM Assistant

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

export interface QueryRequest {
  query: string;
  sessionId?: string;
  timeRange?: string;
}

export interface QueryResponse {
  success: boolean;
  query: string;
  intent: string;
  entities: Array<{
    type: string;
    value: string;
    confidence: number;
  }>;
  results: any;
  summary?: string;
  charts?: any[];
  dslQuery?: any;
  executionTimeMs?: number;
}

class APIService {
  async query(request: QueryRequest): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
  
  async clearContext(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/clear-context?session_id=${sessionId}`, {
      method: 'POST',
    });
    return response.json();
  }
}

export const apiService = new APIService();
