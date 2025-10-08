/**
 * Notification System
 * User-friendly toast notifications and alerts for the SIEM application
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { X, AlertTriangle, CheckCircle, Info, AlertCircle, Wifi, WifiOff } from 'lucide-react';

// ============= TYPES =============

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'loading';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  timestamp: number;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  // Convenience methods
  showSuccess: (title: string, message: string, options?: Partial<Notification>) => string;
  showError: (title: string, message: string, options?: Partial<Notification>) => string;
  showWarning: (title: string, message: string, options?: Partial<Notification>) => string;
  showInfo: (title: string, message: string, options?: Partial<Notification>) => string;
  showLoading: (title: string, message: string, options?: Partial<Notification>) => string;
}

// ============= CONTEXT =============

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

// ============= PROVIDER =============

interface NotificationProviderProps {
  children: React.ReactNode;
  maxNotifications?: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ 
  children, 
  maxNotifications = 5 
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const generateId = () => `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = generateId();
    const newNotification: Notification = {
      id,
      timestamp: Date.now(),
      duration: notification.type === 'loading' ? 0 : notification.duration ?? 5000,
      ...notification,
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      // Remove oldest notifications if exceeding max
      return updated.slice(0, maxNotifications);
    });

    // Auto-remove non-persistent notifications
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // Convenience methods
  const showSuccess = (title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'success', title, message, ...options });
  };

  const showError = (title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({ 
      type: 'error', 
      title, 
      message, 
      duration: 8000, // Errors stay longer
      ...options 
    });
  };

  const showWarning = (title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'warning', title, message, ...options });
  };

  const showInfo = (title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({ type: 'info', title, message, ...options });
  };

  const showLoading = (title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({ 
      type: 'loading', 
      title, 
      message, 
      persistent: true,
      ...options 
    });
  };

  const value: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
};

// ============= NOTIFICATION CONTAINER =============

const NotificationContainer: React.FC = () => {
  const { notifications } = useNotifications();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md w-full">
      {notifications.map((notification) => (
        <NotificationItem key={notification.id} notification={notification} />
      ))}
    </div>
  );
};

// ============= NOTIFICATION ITEM =============

interface NotificationItemProps {
  notification: Notification;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification }) => {
  const { removeNotification } = useNotifications();
  const [isExiting, setIsExiting] = useState(false);

  const handleRemove = () => {
    setIsExiting(true);
    setTimeout(() => removeNotification(notification.id), 300);
  };

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-400" />;
      case 'loading':
        return (
          <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
        );
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  const getBorderColor = () => {
    switch (notification.type) {
      case 'success':
        return 'border-green-500/30';
      case 'error':
        return 'border-red-500/30';
      case 'warning':
        return 'border-yellow-500/30';
      case 'info':
        return 'border-blue-500/30';
      case 'loading':
        return 'border-blue-500/30';
      default:
        return 'border-gray-500/30';
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-900/20';
      case 'error':
        return 'bg-red-900/20';
      case 'warning':
        return 'bg-yellow-900/20';
      case 'info':
        return 'bg-blue-900/20';
      case 'loading':
        return 'bg-blue-900/20';
      default:
        return 'bg-gray-900/20';
    }
  };

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
        bg-gray-800 backdrop-blur-sm border ${getBorderColor()} ${getBackgroundColor()}
        rounded-lg p-4 shadow-lg
      `}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-white mb-1">
            {notification.title}
          </h4>
          <p className="text-sm text-gray-300 leading-relaxed">
            {notification.message}
          </p>
          
          {notification.action && (
            <button
              onClick={notification.action.onClick}
              className="mt-2 text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
            >
              {notification.action.label}
            </button>
          )}
        </div>

        {!notification.persistent && (
          <button
            onClick={handleRemove}
            className="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Progress bar for timed notifications */}
      {notification.duration && notification.duration > 0 && (
        <div className="mt-3">
          <div 
            className={`h-1 bg-current opacity-30 rounded-full ${
              notification.type === 'success' ? 'text-green-400' :
              notification.type === 'error' ? 'text-red-400' :
              notification.type === 'warning' ? 'text-yellow-400' :
              'text-blue-400'
            }`}
            style={{
              animation: `shrink ${notification.duration}ms linear forwards`
            }}
          />
        </div>
      )}
    </div>
  );
};

// ============= CONNECTION STATUS =============

export const ConnectionStatus: React.FC = () => {
  const { showError, showSuccess } = useNotifications();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [hasShownOffline, setHasShownOffline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setHasShownOffline(false);
      showSuccess(
        'Connection Restored',
        'SIEM application is back online'
      );
    };

    const handleOffline = () => {
      setIsOnline(false);
      if (!hasShownOffline) {
        setHasShownOffline(true);
        showError(
          'Connection Lost',
          'SIEM application is offline. Some features may not work.',
          { persistent: true }
        );
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [showError, showSuccess, hasShownOffline]);

  if (!isOnline) {
    return (
      <div className="fixed bottom-4 left-4 bg-red-900/90 border border-red-700 rounded-lg p-3 backdrop-blur-sm">
        <div className="flex items-center space-x-2">
          <WifiOff className="w-4 h-4 text-red-400" />
          <span className="text-sm text-white">Offline</span>
        </div>
      </div>
    );
  }

  return null;
};

// ============= ERROR NOTIFICATION HELPERS =============

export const createApiErrorNotification = (error: any, context?: string): Omit<Notification, 'id' | 'timestamp'> => {
  const isNetworkError = !error.response;
  const statusCode = error.response?.status;
  
  let title = 'API Error';
  let message = 'An error occurred while communicating with the server.';

  if (context) {
    title = `${context} Error`;
  }

  if (isNetworkError) {
    message = 'Unable to connect to the SIEM server. Please check your internet connection.';
  } else if (statusCode === 401) {
    title = 'Authentication Error';
    message = 'Your session has expired. Please log in again.';
  } else if (statusCode === 403) {
    title = 'Permission Denied';
    message = 'You do not have permission to perform this action.';
  } else if (statusCode === 404) {
    title = 'Not Found';
    message = 'The requested resource was not found.';
  } else if (statusCode === 429) {
    title = 'Rate Limited';
    message = 'Too many requests. Please wait a moment before trying again.';
  } else if (statusCode >= 500) {
    title = 'Server Error';
    message = 'The SIEM server encountered an error. Please try again later.';
  } else if (error.message) {
    message = error.message;
  }

  return {
    type: 'error',
    title,
    message,
    duration: 8000,
    action: statusCode === 401 ? {
      label: 'Log In',
      onClick: () => window.location.href = '/login'
    } : undefined
  };
};

// ============= STYLED NOTIFICATION VARIANTS =============

export const SecurityAlertNotification: React.FC<{
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  onView?: () => void;
}> = ({ severity, title, message, onView }) => {
  const { addNotification } = useNotifications();

  React.useEffect(() => {
    const severityConfig = {
      critical: { type: 'error' as const, duration: 0, persistent: true },
      high: { type: 'error' as const, duration: 10000 },
      medium: { type: 'warning' as const, duration: 8000 },
      low: { type: 'info' as const, duration: 6000 }
    };

    const config = severityConfig[severity];

    addNotification({
      ...config,
      title: `🚨 ${title}`,
      message,
      action: onView ? {
        label: 'View Details',
        onClick: onView
      } : undefined
    });
  }, [severity, title, message, onView, addNotification]);

  return null;
};

// ============= CSS ANIMATION =============

const styles = `
@keyframes shrink {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}

// ============= EXPORTS =============

export default NotificationProvider;
