/**
 * KARTAVYA SIEM - Global State Management
 * Zustand store for complete application state
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { SecurityAlert, DashboardMetrics, SystemStatus } from '../services/api.service';

// User interface for auth
export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department?: string;
  lastLogin?: string;
  avatar?: string;
}

// ============= INTERFACES =============

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface AppState {
  // UI State
  activeTab: string;
  sidebarCollapsed: boolean;
  theme: 'dark' | 'light';
  notifications: Notification[];
  
  // Connection State
  isConnected: boolean;
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error';
  lastPing: Date | null;
  
  // Data State
  dashboardMetrics: DashboardMetrics | null;
  systemStatus: SystemStatus | null;
  alerts: SecurityAlert[];
  unreadAlertCount: number;
  
  // Chat State
  currentSessionId: string;
  chatHistory: any[];
  
  // Loading States
  loadingStates: {
    dashboard: boolean;
    chat: boolean;
    reports: boolean;
    alerts: boolean;
  };
  
  // Error States
  errors: {
    dashboard: string | null;
    chat: string | null;
    reports: string | null;
    alerts: string | null;
  };
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  autoClose?: number;
}

// Combined store interface
export interface StoreState extends AuthState, AppState {
  // Auth Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  setAuthLoading: (loading: boolean) => void;
  setAuthError: (error: string | null) => void;
  
  // UI Actions
  setActiveTab: (tab: string) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  markNotificationRead: (id: string) => void;
  clearAllNotifications: () => void;
  
  // Connection Actions
  setConnectionStatus: (status: 'connected' | 'connecting' | 'disconnected' | 'error') => void;
  updateLastPing: () => void;
  
  // Data Actions
  setDashboardMetrics: (metrics: DashboardMetrics | null) => void;
  setSystemStatus: (status: SystemStatus | null) => void;
  setAlerts: (alerts: SecurityAlert[]) => void;
  markAlertAsRead: (alertId: string) => void;
  updateUnreadAlertCount: () => void;
  
  // Chat Actions
  setChatHistory: (history: any[]) => void;
  addChatMessage: (message: any) => void;
  clearChatHistory: () => void;
  setCurrentSessionId: (sessionId: string) => void;
  
  // Loading Actions
  setLoading: (key: keyof AppState['loadingStates'], loading: boolean) => void;
  
  // Error Actions
  setError: (key: keyof AppState['errors'], error: string | null) => void;
  clearAllErrors: () => void;
  
  // Utility Actions
  reset: () => void;
  refreshData: () => void;
}

// ============= STORE IMPLEMENTATION =============

const initialState: Omit<StoreState, 'login' | 'logout' | 'setUser' | 'setAuthLoading' | 'setAuthError' | 'setActiveTab' | 'toggleSidebar' | 'setTheme' | 'addNotification' | 'removeNotification' | 'markNotificationRead' | 'clearAllNotifications' | 'setConnectionStatus' | 'updateLastPing' | 'setDashboardMetrics' | 'setSystemStatus' | 'setAlerts' | 'markAlertAsRead' | 'updateUnreadAlertCount' | 'setChatHistory' | 'addChatMessage' | 'clearChatHistory' | 'setCurrentSessionId' | 'setLoading' | 'setError' | 'clearAllErrors' | 'reset' | 'refreshData'> = {
  // Auth State
  isAuthenticated: false,
  user: null,
  token: null,
  loading: false,
  error: null,
  
  // UI State
  activeTab: 'chat',
  sidebarCollapsed: false,
  theme: 'dark',
  notifications: [],
  
  // Connection State
  isConnected: false,
  connectionStatus: 'disconnected',
  lastPing: null,
  
  // Data State
  dashboardMetrics: null,
  systemStatus: null,
  alerts: [],
  unreadAlertCount: 0,
  
  // Chat State
  currentSessionId: `session_${Date.now()}`,
  chatHistory: [],
  
  // Loading States
  loadingStates: {
    dashboard: false,
    chat: false,
    reports: false,
    alerts: false,
  },
  
  // Error States
  errors: {
    dashboard: null,
    chat: null,
    reports: null,
    alerts: null,
  },
};

export const useAppStore = create<StoreState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // ============= AUTH ACTIONS =============
        
        login: async (email: string, password: string) => {
          set({ loading: true, error: null });
          try {
            // Import API service dynamically to avoid circular imports
            const { default: apiService } = await import('../services/api.service');
            const response = await apiService.login(email, password);
            
            set({
              isAuthenticated: true,
              user: response.user,
              token: response.token,
              loading: false,
              error: null,
            });
            
            get().addNotification({
              type: 'success',
              title: 'Login Successful',
              message: `Welcome back, ${response.user.name}!`,
              read: false,
              autoClose: 5000,
            });
            
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Login failed';
            set({
              loading: false,
              error: message,
            });
            
            get().addNotification({
              type: 'error',
              title: 'Login Failed',
              message,
              read: false,
            });
            throw error; // Re-throw so components can handle it
          }
        },
        
        logout: () => {
          // Clear auth state
          set({
            isAuthenticated: false,
            user: null,
            token: null,
            loading: false,
            error: null,
          });
          
          // Clear sensitive data
          get().clearChatHistory();
          
          // Clear localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          
          get().addNotification({
            type: 'info',
            title: 'Logged Out',
            message: 'You have been successfully logged out.',
            read: false,
            autoClose: 3000,
          });
        },
        
        setUser: (user) => set({ user }),
        setAuthLoading: (loading) => set({ loading }),
        setAuthError: (error) => set({ error }),
        
        // ============= UI ACTIONS =============
        
        setActiveTab: (tab) => set({ activeTab: tab }),
        
        toggleSidebar: () => set((state) => ({ 
          sidebarCollapsed: !state.sidebarCollapsed 
        })),
        
        setTheme: (theme) => set({ theme }),
        
        addNotification: (notification) => {
          const newNotification: Notification = {
            ...notification,
            id: `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date(),
          };
          
          set((state) => ({
            notifications: [newNotification, ...state.notifications].slice(0, 50) // Keep max 50
          }));
          
          // Auto-remove if specified
          if (notification.autoClose) {
            setTimeout(() => {
              get().removeNotification(newNotification.id);
            }, notification.autoClose);
          }
        },
        
        removeNotification: (id) => set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        })),
        
        markNotificationRead: (id) => set((state) => ({
          notifications: state.notifications.map(n => 
            n.id === id ? { ...n, read: true } : n
          )
        })),
        
        clearAllNotifications: () => set({ notifications: [] }),
        
        // ============= CONNECTION ACTIONS =============
        
        setConnectionStatus: (status) => {
          set({ 
            connectionStatus: status,
            isConnected: status === 'connected'
          });
          
          if (status === 'connected') {
            get().updateLastPing();
          }
        },
        
        updateLastPing: () => set({ lastPing: new Date() }),
        
        // ============= DATA ACTIONS =============
        
        setDashboardMetrics: (metrics) => set({ dashboardMetrics: metrics }),
        
        setSystemStatus: (status) => set({ systemStatus: status }),
        
        setAlerts: (alerts) => {
          set({ alerts });
          get().updateUnreadAlertCount();
        },
        
        markAlertAsRead: (alertId) => {
          set((state) => ({
            alerts: state.alerts.map(alert => 
              alert.id === alertId ? { ...alert, status: 'investigating' } : alert
            )
          }));
          get().updateUnreadAlertCount();
        },
        
        updateUnreadAlertCount: () => {
          const { alerts } = get();
          const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
          const unreadCount = alerts.filter(alert => 
            new Date(alert.time) > fiveMinutesAgo && alert.status === 'open'
          ).length;
          
          set({ unreadAlertCount: unreadCount });
        },
        
        // ============= CHAT ACTIONS =============
        
        setChatHistory: (history) => set({ chatHistory: history }),
        
        addChatMessage: (message) => set((state) => ({
          chatHistory: [...state.chatHistory, message]
        })),
        
        clearChatHistory: () => set({ 
          chatHistory: [],
          currentSessionId: `session_${Date.now()}`
        }),
        
        setCurrentSessionId: (sessionId) => set({ currentSessionId: sessionId }),
        
        // ============= LOADING ACTIONS =============
        
        setLoading: (key, loading) => set((state) => ({
          loadingStates: {
            ...state.loadingStates,
            [key]: loading
          }
        })),
        
        // ============= ERROR ACTIONS =============
        
        setError: (key, error) => set((state) => ({
          errors: {
            ...state.errors,
            [key]: error
          }
        })),
        
        clearAllErrors: () => set({
          errors: {
            dashboard: null,
            chat: null,
            reports: null,
            alerts: null,
          }
        }),
        
        // ============= UTILITY ACTIONS =============
        
        reset: () => set(initialState),
        
        refreshData: async () => {
          const store = get();
          
          // Add refresh notification
          store.addNotification({
            type: 'info',
            title: 'Refreshing Data',
            message: 'Updating all dashboard data...',
            read: false,
            autoClose: 2000,
          });
          
          // This would trigger data refresh hooks
          // The actual data fetching is handled by hooks
        },
      }),
      {
        name: 'kartavya-siem-store',
        partialize: (state) => ({
          // Only persist UI preferences and auth state
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          user: state.user,
          token: state.token,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    {
      name: 'kartavya-siem-store',
    }
  )
);

// ============= SELECTORS =============

// Auth selectors
export const useAuth = () => useAppStore((state) => ({
  isAuthenticated: state.isAuthenticated,
  user: state.user,
  loading: state.loading,
  error: state.error,
  login: state.login,
  logout: state.logout,
}));

// UI selectors
export const useUI = () => useAppStore((state) => ({
  activeTab: state.activeTab,
  sidebarCollapsed: state.sidebarCollapsed,
  theme: state.theme,
  setActiveTab: state.setActiveTab,
  toggleSidebar: state.toggleSidebar,
  setTheme: state.setTheme,
}));

// Connection selectors
export const useConnection = () => useAppStore((state) => ({
  isConnected: state.isConnected,
  connectionStatus: state.connectionStatus,
  lastPing: state.lastPing,
  setConnectionStatus: state.setConnectionStatus,
  updateLastPing: state.updateLastPing,
}));

// Data selectors
export const useDashboard = () => useAppStore((state) => ({
  metrics: state.dashboardMetrics,
  systemStatus: state.systemStatus,
  setDashboardMetrics: state.setDashboardMetrics,
  setSystemStatus: state.setSystemStatus,
}));

// Alert selectors
export const useAlerts = () => useAppStore((state) => ({
  alerts: state.alerts,
  unreadCount: state.unreadAlertCount,
  setAlerts: state.setAlerts,
  markAsRead: state.markAlertAsRead,
}));

// Notification selectors
export const useNotifications = () => useAppStore((state) => ({
  notifications: state.notifications,
  addNotification: state.addNotification,
  removeNotification: state.removeNotification,
  markNotificationRead: state.markNotificationRead,
  clearAllNotifications: state.clearAllNotifications,
}));

// Loading selectors
export const useLoading = () => useAppStore((state) => ({
  loadingStates: state.loadingStates,
  setLoading: state.setLoading,
}));

// Error selectors
export const useErrors = () => useAppStore((state) => ({
  errors: state.errors,
  setError: state.setError,
  clearAllErrors: state.clearAllErrors,
}));

export default useAppStore;
