/**
 * Custom Hooks for API Data Fetching
 * Real-time data with proper loading and error states
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiService, { 
  DashboardMetrics, 
  SystemStatus, 
  ChatResponse, 
  Report, 
  SecurityAlert 
} from '../services/api.service';

// Generic hook for API calls with caching
export function useApiData<T>(
  fetcher: () => Promise<T>,
  dependencies: any[] = [],
  options: {
    refreshInterval?: number;
    enabled?: boolean;
    retryCount?: number;
  } = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const retryCountRef = useRef(0);
  const intervalRef = useRef<NodeJS.Timeout>();

  const { refreshInterval, enabled = true, retryCount = 3 } = options;

  const fetchData = useCallback(async () => {
    if (!enabled) return;
    
    try {
      setLoading(true);
      setError(null);
      const result = await fetcher();
      setData(result);
      retryCountRef.current = 0;
    } catch (err) {
      console.error('API fetch error:', err);
      
      // Retry logic
      if (retryCountRef.current < retryCount) {
        retryCountRef.current++;
        setTimeout(() => fetchData(), 1000 * retryCountRef.current);
      } else {
        setError(err instanceof Error ? err : new Error('Failed to fetch data'));
      }
    } finally {
      setLoading(false);
    }
  }, [fetcher, enabled, retryCount]);

  useEffect(() => {
    fetchData();

    // Set up refresh interval if specified
    if (refreshInterval && refreshInterval > 0) {
      intervalRef.current = setInterval(fetchData, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [...dependencies, enabled]);

  const refetch = useCallback(() => {
    retryCountRef.current = 0;
    return fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
}

// Hook for dashboard metrics with real-time updates
export function useDashboardMetrics(refreshInterval = 30000) {
  return useApiData(
    () => apiService.getDashboardMetrics(),
    [],
    { refreshInterval }
  );
}

// Hook for system status
export function useSystemStatus(refreshInterval = 10000) {
  return useApiData(
    () => apiService.getSystemStatus(),
    [],
    { refreshInterval }
  );
}

// Hook for chat functionality
export function useChat() {
  const [messages, setMessages] = useState<ChatResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = useCallback(async (query: string, filters?: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.sendChatMessage(query, filters);
      setMessages(prev => [...prev, response]);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to send message');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      await apiService.clearChatHistory();
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const history = await apiService.getChatHistory();
      if (history?.messages) {
        setMessages(history.messages);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
    loadHistory
  };
}

// Hook for reports
export function useReports() {
  return useApiData(
    () => apiService.getReports(),
    [],
    { refreshInterval: 60000 }
  );
}

// Hook for generating reports
export function useReportGenerator() {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const generateReport = useCallback(async (type: string, config: any) => {
    setGenerating(true);
    setError(null);
    
    try {
      const report = await apiService.generateReport(type, config);
      return report;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to generate report');
      setError(error);
      throw error;
    } finally {
      setGenerating(false);
    }
  }, []);

  return { generateReport, generating, error };
}

// Hook for real-time alerts
export function useAlerts(refreshInterval = 5000) {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const { data: metrics, loading, error } = useDashboardMetrics(refreshInterval);

  useEffect(() => {
    if (metrics?.recentAlerts) {
      setAlerts(metrics.recentAlerts);
      
      // Count unread alerts (those less than 5 minutes old)
      const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
      const unread = metrics.recentAlerts.filter(alert => {
        const alertTime = new Date(alert.time).getTime();
        return alertTime > fiveMinutesAgo;
      }).length;
      
      setUnreadCount(unread);
    }
  }, [metrics]);

  const markAsRead = useCallback((alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, status: 'investigating' as const }
          : alert
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  return {
    alerts,
    unreadCount,
    loading,
    error,
    markAsRead
  };
}

// Hook for query execution
export function useQuery() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const executeQuery = useCallback(async (query: string, filters?: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.executeQuery(query, filters);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Query execution failed');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return { executeQuery, loading, error };
}

// Hook for connection status
export function useConnectionStatus() {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  const checkConnection = useCallback(async () => {
    try {
      setIsChecking(true);
      const status = await apiService.getSystemStatus();
      setIsConnected(status.status === 'healthy');
    } catch {
      setIsConnected(false);
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    checkConnection();
    
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, [checkConnection]);

  return { isConnected, isChecking, checkConnection };
}

// Hook for dataset testing
export function useDatasetStatus() {
  const [datasets, setDatasets] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  const testDatasets = useCallback(async () => {
    setTesting(true);
    try {
      const result = await apiService.testDatasets();
      setDatasets(result);
      return result;
    } catch (err) {
      console.error('Dataset test failed:', err);
      return null;
    } finally {
      setTesting(false);
    }
  }, []);

  useEffect(() => {
    testDatasets();
  }, []);

  return { datasets, testing, testDatasets };
}

// Hook for polling with exponential backoff
export function usePolling<T>(
  fetcher: () => Promise<T>,
  options: {
    interval?: number;
    maxInterval?: number;
    enabled?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const intervalRef = useRef<NodeJS.Timeout>();
  const currentIntervalRef = useRef(options.interval || 5000);

  const {
    interval = 5000,
    maxInterval = 60000,
    enabled = true,
    onSuccess,
    onError
  } = options;

  useEffect(() => {
    if (!enabled) return;

    const poll = async () => {
      try {
        const result = await fetcher();
        setData(result);
        setError(null);
        currentIntervalRef.current = interval; // Reset interval on success
        onSuccess?.(result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Polling failed');
        setError(error);
        onError?.(error);
        
        // Exponential backoff
        currentIntervalRef.current = Math.min(
          currentIntervalRef.current * 2,
          maxInterval
        );
      }
      
      // Schedule next poll
      intervalRef.current = setTimeout(poll, currentIntervalRef.current);
    };

    // Initial poll
    poll();

    return () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
      }
    };
  }, [fetcher, interval, maxInterval, enabled, onSuccess, onError]);

  return { data, error };
}

export default {
  useApiData,
  useDashboardMetrics,
  useSystemStatus,
  useChat,
  useReports,
  useReportGenerator,
  useAlerts,
  useQuery,
  useConnectionStatus,
  useDatasetStatus,
  usePolling
};
