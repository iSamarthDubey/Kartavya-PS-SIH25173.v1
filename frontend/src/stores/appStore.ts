/**
 * App Store - Global application state management
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, UIState, SiemConnector } from '@/types'
import { authApi, systemApi, adminApi } from '@/services/api'

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read?: boolean
  action?: {
    label: string
    handler: () => void
  }
}

interface AppState {
  // Auth state
  user: User | null
  token: string | null
  isAuthenticated: boolean
  
  // UI state
  mode: 'landing' | 'dashboard' | 'chat' | 'hybrid' | 'reports' | 'investigations' | 'admin'
  sidebarCollapsed: boolean
  chatPanelOpen: boolean
  loading: boolean
  error: string | null
  
  // System state
  systemHealth: any | null
  connectors: SiemConnector[]
  
  // Theme and preferences
  theme: 'dark' | 'light'
  
  // Notifications
  notifications: Notification[]
  
  // Actions
  login: (identifier: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  
  // UI actions
  setMode: (mode: AppState['mode']) => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleChatPanel: () => void
  setChatPanelOpen: (open: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  
  // System actions
  checkSystemHealth: () => Promise<void>
  loadConnectors: () => Promise<void>
  
  // Theme actions
  setTheme: (theme: 'dark' | 'light') => void
  toggleTheme: () => void
  
  // Notification actions
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  markNotificationAsRead: (id: string) => void
  clearNotifications: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      
      mode: 'dashboard',
      sidebarCollapsed: false,
      chatPanelOpen: false,
      loading: false,
      error: null,
      
      systemHealth: null,
      connectors: [],
      
      theme: 'dark',
      notifications: [],

      // Auth actions
      login: async (identifier: string, password: string) => {
        try {
          set({ loading: true, error: null })
          
          const response = await authApi.login({ email: identifier, password })
          
          if (response.success && response.token && response.user) {
            const { token, user } = response
            
            set({
              user,
              token,
              isAuthenticated: true,
              loading: false,
              mode: 'dashboard'
            })
            
            // Store token in localStorage for axios interceptor
            localStorage.setItem('synrgy_token', token)
            
            // Load initial data
            get().checkSystemHealth()
            get().loadConnectors()
          }
        } catch (error: any) {
          console.error('Login failed:', error)
          set({
            error: error.response?.data?.message || error.message || 'Login failed',
            loading: false
          })
          throw error
        }
      },

      logout: () => {
        // Call logout API (don't await to avoid blocking)
        authApi.logout().catch(console.error)
        
        // Clear local state
        localStorage.removeItem('synrgy_token')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          mode: 'landing',
          error: null
        })
      },

      setUser: (user: User | null) => {
        set({ 
          user, 
          isAuthenticated: !!user 
        })
      },

      setToken: (token: string | null) => {
        set({ token, isAuthenticated: !!token })
        
        if (token) {
          localStorage.setItem('synrgy_token', token)
        } else {
          localStorage.removeItem('synrgy_token')
        }
      },

      // UI actions
      setMode: (mode: AppState['mode']) => {
        set({ mode })
        
        // Auto-open chat panel in hybrid mode
        if (mode === 'hybrid') {
          set({ chatPanelOpen: true })
        }
      },

      toggleSidebar: () => {
        set(state => ({ sidebarCollapsed: !state.sidebarCollapsed }))
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed })
      },

      toggleChatPanel: () => {
        set(state => ({ chatPanelOpen: !state.chatPanelOpen }))
      },

      setChatPanelOpen: (open: boolean) => {
        set({ chatPanelOpen: open })
      },

      setLoading: (loading: boolean) => {
        set({ loading })
      },

      setError: (error: string | null) => {
        set({ error })
      },

      clearError: () => {
        set({ error: null })
      },

      // System actions
      checkSystemHealth: async () => {
        try {
          const health = await systemApi.health()
          set({ systemHealth: health })
        } catch (error) {
          console.warn('Failed to check system health:', error)
          // Don't set error state for health check failures
        }
      },

      loadConnectors: async () => {
        try {
          const response = await adminApi.getConnectors()
          set({ connectors: response.data || [] })
        } catch (error) {
          console.warn('Failed to load connectors:', error)
          // Don't set error state for connector load failures
        }
      },

      // Theme actions
      setTheme: (theme: 'dark' | 'light') => {
        set({ theme })
        
        // Update document class for Tailwind dark mode (only if in browser)
        if (typeof document !== 'undefined' && document.documentElement) {
          if (theme === 'dark') {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
        }
      },

      toggleTheme: () => {
        const currentTheme = get().theme
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
        get().setTheme(newTheme)
      },
      
      // Notification actions
      addNotification: (notification: Omit<Notification, 'id'>) => {
        const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        const newNotification: Notification = {
          id,
          ...notification,
          read: false
        }
        
        set(state => ({
          notifications: [newNotification, ...state.notifications].slice(0, 50) // Keep max 50 notifications
        }))
        
        // Auto-remove success and info notifications after 5 seconds
        if (notification.type === 'success' || notification.type === 'info') {
          setTimeout(() => {
            get().removeNotification(id)
          }, 5000)
        }
      },
      
      removeNotification: (id: string) => {
        set(state => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }))
      },
      
      markNotificationAsRead: (id: string) => {
        set(state => ({
          notifications: state.notifications.map(n => 
            n.id === id ? { ...n, read: true } : n
          )
        }))
      },
      
      clearNotifications: () => {
        set({ notifications: [] })
      }
    }),
    {
      name: 'synrgy-app-store',
      partialize: (state) => ({
        // Persist only essential data
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        mode: state.mode,
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme
      }),
      onRehydrateStorage: () => (state) => {
        // Initialize theme on rehydration
        if (state?.theme && typeof document !== 'undefined' && document.documentElement) {
          if (state.theme === 'dark') {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
        }
        
        // Check authentication status
        if (state?.isAuthenticated && state?.token) {
          // Verify token is still valid
          authApi.me().catch(() => {
            // Token is invalid, logout
            state.logout?.()
          })
        }
      }
    }
  )
)

// Selectors
export const useAuth = () => {
  return useAppStore(state => ({
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    login: state.login,
    logout: state.logout
  }))
}

export const useUIState = (): UIState => {
  return useAppStore(state => ({
    mode: state.mode,
    sidebar_collapsed: state.sidebarCollapsed,
    chat_panel_open: state.chatPanelOpen,
    loading: state.loading,
    error: state.error
  }))
}

export const useSystemInfo = () => {
  return useAppStore(state => ({
    systemHealth: state.systemHealth,
    connectors: state.connectors,
    checkSystemHealth: state.checkSystemHealth,
    loadConnectors: state.loadConnectors
  }))
}

export const useTheme = () => {
  return useAppStore(state => ({
    theme: state.theme,
    setTheme: state.setTheme,
    toggleTheme: state.toggleTheme
  }))
}
