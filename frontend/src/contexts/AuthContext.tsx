import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { api } from '../services/api';

// User roles and permissions
export type UserRole = 'admin' | 'analyst' | 'viewer' | 'incident_responder' | 'compliance_officer';

export interface Permission {
  resource: string;
  actions: string[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  profile: {
    firstName: string;
    lastName: string;
    department: string;
    avatar?: string;
    lastLogin: string;
    createdAt: string;
  };
  preferences: {
    theme: 'dark' | 'light';
    language: string;
    timezone: string;
    notifications: boolean;
  };
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  sessionExpiry: number | null;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string; expiresIn: number } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<User> }
  | { type: 'CLEAR_ERROR' };

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  loading: true,
  error: null,
  sessionExpiry: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        loading: false,
        error: null,
        sessionExpiry: Date.now() + action.payload.expiresIn * 1000,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        loading: false,
        error: action.payload,
        sessionExpiry: null,
      };
    case 'LOGOUT':
      return {
        ...initialState,
        loading: false,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  hasPermission: (resource: string, action: string) => boolean;
  hasRole: (roles: UserRole | UserRole[]) => boolean;
  clearError: () => void;
  refreshToken: () => Promise<void>;
}

export interface LoginCredentials {
  username: string;
  password: string;
  mfaToken?: string;
  rememberMe?: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Role hierarchy and default permissions
const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  admin: [
    { resource: '*', actions: ['*'] }, // Full access
  ],
  analyst: [
    { resource: 'dashboard', actions: ['read'] },
    { resource: 'investigations', actions: ['read', 'create', 'update'] },
    { resource: 'reports', actions: ['read', 'create'] },
    { resource: 'alerts', actions: ['read', 'update'] },
    { resource: 'queries', actions: ['read', 'create'] },
    { resource: 'incidents', actions: ['read', 'create', 'update'] },
  ],
  incident_responder: [
    { resource: 'dashboard', actions: ['read'] },
    { resource: 'investigations', actions: ['read', 'create', 'update'] },
    { resource: 'incidents', actions: ['read', 'create', 'update', 'delete'] },
    { resource: 'alerts', actions: ['read', 'update', 'resolve'] },
    { resource: 'forensics', actions: ['read', 'create'] },
  ],
  compliance_officer: [
    { resource: 'dashboard', actions: ['read'] },
    { resource: 'reports', actions: ['read', 'create'] },
    { resource: 'audit_logs', actions: ['read'] },
    { resource: 'compliance', actions: ['read', 'create', 'update'] },
    { resource: 'policies', actions: ['read', 'update'] },
  ],
  viewer: [
    { resource: 'dashboard', actions: ['read'] },
    { resource: 'reports', actions: ['read'] },
    { resource: 'alerts', actions: ['read'] },
  ],
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('auth_token');
      const userStr = localStorage.getItem('user_data');
      const expiry = localStorage.getItem('session_expiry');

      if (token && userStr && expiry) {
        const expiryTime = parseInt(expiry);
        if (Date.now() < expiryTime) {
          try {
            const user = JSON.parse(userStr);
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: {
                user,
                token,
                expiresIn: Math.floor((expiryTime - Date.now()) / 1000),
              },
            });
          } catch (error) {
            console.error('Error parsing user data:', error);
            logout();
          }
        } else {
          logout();
        }
      } else {
        dispatch({ type: 'AUTH_FAILURE', payload: 'No valid session found' });
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (state.sessionExpiry && state.isAuthenticated) {
      const refreshTime = state.sessionExpiry - 5 * 60 * 1000; // Refresh 5 minutes before expiry
      const now = Date.now();

      if (refreshTime > now) {
        const timeout = setTimeout(() => {
          refreshToken();
        }, refreshTime - now);

        return () => clearTimeout(timeout);
      }
    }
  }, [state.sessionExpiry, state.isAuthenticated]);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'AUTH_START' });

    try {
      const response = await api.post('/auth/login', credentials);
      const { user, token, expiresIn } = response.data;

      // Store in localStorage
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_data', JSON.stringify(user));
      localStorage.setItem('session_expiry', (Date.now() + expiresIn * 1000).toString());

      // Set default permissions based on role
      const userWithPermissions = {
        ...user,
        permissions: user.permissions || ROLE_PERMISSIONS[user.role] || [],
      };

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: userWithPermissions, token, expiresIn },
      });

      // Set auth header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('session_expiry');

    // Clear auth header
    delete api.defaults.headers.common['Authorization'];

    dispatch({ type: 'LOGOUT' });
  };

  const updateUser = (userData: Partial<User>) => {
    if (state.user) {
      const updatedUser = { ...state.user, ...userData };
      localStorage.setItem('user_data', JSON.stringify(updatedUser));
      dispatch({ type: 'UPDATE_USER', payload: userData });
    }
  };

  const hasPermission = (resource: string, action: string): boolean => {
    if (!state.user || !state.isAuthenticated) return false;

    return state.user.permissions.some((permission) => {
      // Admin wildcard access
      if (permission.resource === '*' && permission.actions.includes('*')) {
        return true;
      }

      // Exact resource match
      if (permission.resource === resource) {
        return permission.actions.includes(action) || permission.actions.includes('*');
      }

      // Wildcard resource match
      if (permission.resource.endsWith('*')) {
        const baseResource = permission.resource.slice(0, -1);
        if (resource.startsWith(baseResource)) {
          return permission.actions.includes(action) || permission.actions.includes('*');
        }
      }

      return false;
    });
  };

  const hasRole = (roles: UserRole | UserRole[]): boolean => {
    if (!state.user || !state.isAuthenticated) return false;

    const userRole = state.user.role;
    if (Array.isArray(roles)) {
      return roles.includes(userRole);
    }
    return userRole === roles;
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const response = await api.post('/auth/refresh');
      const { token, expiresIn } = response.data;

      localStorage.setItem('auth_token', token);
      localStorage.setItem('session_expiry', (Date.now() + expiresIn * 1000).toString());

      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      if (state.user) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: { user: state.user, token, expiresIn },
        });
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
    }
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    updateUser,
    hasPermission,
    hasRole,
    clearError,
    refreshToken,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Higher-order component for protecting routes
export const ProtectedRoute: React.FC<{
  children: ReactNode;
  requireAuth?: boolean;
  requiredPermission?: { resource: string; action: string };
  requiredRole?: UserRole | UserRole[];
  fallback?: ReactNode;
}> = ({
  children,
  requireAuth = true,
  requiredPermission,
  requiredRole,
  fallback = <div>Access Denied</div>,
}) => {
  const { isAuthenticated, hasPermission, hasRole } = useAuth();

  if (requireAuth && !isAuthenticated) {
    return <>{fallback}</>;
  }

  if (requiredPermission && !hasPermission(requiredPermission.resource, requiredPermission.action)) {
    return <>{fallback}</>;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
