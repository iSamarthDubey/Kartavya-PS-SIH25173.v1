/**
 * SYNRGY Auth Provider
 * Handles JWT authentication, user management, and RBAC
 * Based on SYNRGY.TXT security specifications
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '@/services/api'
import { toast } from 'react-hot-toast'
import { performanceMonitor } from '@/services/performance'

interface User {
  id: string
  username: string
  email: string
  full_name: string
  role: string
  department: string
  location: string
  permissions: string[]
  security_clearance: string
  last_login?: string
  preferences: Record<string, any>
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (identifier: string, password: string) => Promise<boolean>
  logout: () => void
  refreshToken: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (role: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('synrgy_token')
      const storedUser = localStorage.getItem('synrgy_user')

      if (storedToken && storedUser) {
        try {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          
          // Set default authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
          
          // Validate token with backend
          await validateToken(storedToken)
        } catch (error) {
          console.error('Token validation failed:', error)
          clearAuth()
        }
      }
      
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  // Set up token refresh interval
  useEffect(() => {
    if (!token) return

    const refreshInterval = setInterval(async () => {
      try {
        await refreshToken()
      } catch (error) {
        console.error('Token refresh failed:', error)
        logout()
      }
    }, 15 * 60 * 1000) // Refresh every 15 minutes

    return () => clearInterval(refreshInterval)
  }, [token])

  const validateToken = async (tokenToValidate: string) => {
    try {
      const response = await api.get('/api/auth/profile', {
        headers: { Authorization: `Bearer ${tokenToValidate}` }
      })
      
      // Profile endpoint returns UserProfile directly, not wrapped in success object
      if (response.data && response.data.username) {
        setUser(response.data)
        return true
      } else {
        throw new Error('Invalid token response')
      }
    } catch (error) {
      throw error
    }
  }

  const login = async (identifier: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      
      const response = await api.post('/api/auth/login', {
        identifier,
        password,
      })

      if (response.data.success && response.data.token) {
        const { token: newToken, user: userData, permissions } = response.data
        
        // Merge permissions into user object
        const userWithPermissions = {
          ...userData,
          permissions: permissions || [],
        }

        setToken(newToken)
        setUser(userWithPermissions)

        // Store in localStorage
        localStorage.setItem('synrgy_token', newToken)
        localStorage.setItem('synrgy_user', JSON.stringify(userWithPermissions))

        // Set default authorization header
        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
        
        // Track user login in performance monitor
        performanceMonitor.setUserId(userWithPermissions.id)

        toast.success(`Welcome back, ${userData.full_name}!`)
        return true
      } else {
        toast.error(response.data.message || 'Login failed')
        return false
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed. Please try again.'
      toast.error(message)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    clearAuth()
    toast.success('Logged out successfully')
    
    // Redirect to login page
    window.location.href = '/login'
  }

  const clearAuth = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('synrgy_token')
    localStorage.removeItem('synrgy_user')
    delete api.defaults.headers.common['Authorization']
  }

  const refreshToken = async () => {
    try {
      const response = await api.post('/api/auth/refresh')
      
      if (response.data.success && response.data.token) {
        const newToken = response.data.token
        setToken(newToken)
        localStorage.setItem('synrgy_token', newToken)
        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      }
    } catch (error) {
      throw error
    }
  }

  const hasPermission = (permission: string): boolean => {
    if (!user || !user.permissions) return false
    return user.permissions.includes(permission) || user.role === 'admin'
  }

  const hasRole = (role: string): boolean => {
    if (!user) return false
    return user.role === role || user.role === 'admin'
  }

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    refreshToken,
    hasPermission,
    hasRole,
  }

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
}
