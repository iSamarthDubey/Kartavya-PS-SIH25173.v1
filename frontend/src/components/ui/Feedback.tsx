/**
 * SYNRGY User Feedback Components
 * Error states, notifications, toasts, and contextual help
 */

import React, { useState, useEffect, createContext, useContext } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  X, 
  RefreshCw, 
  AlertCircle,
  HelpCircle,
  Wifi,
  WifiOff,
  Zap
} from 'lucide-react'

// Toast Types
type ToastType = 'success' | 'error' | 'warning' | 'info'
type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center'

interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

// Toast Context
interface ToastContextType {
  showToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  toasts: Toast[]
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

// Toast Provider
interface ToastProviderProps {
  children: React.ReactNode
  position?: ToastPosition
  maxToasts?: number
}

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  position = 'top-right',
  maxToasts = 5
}) => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = (toast: Omit<Toast, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const newToast: Toast = {
      id,
      duration: 5000,
      ...toast
    }

    setToasts(prev => {
      const updated = [newToast, ...prev].slice(0, maxToasts)
      return updated
    })

    // Auto remove after duration
    if (newToast.duration) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }
  }

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2'
  }

  return (
    <ToastContext.Provider value={{ showToast, removeToast, toasts }}>
      {children}
      
      {/* Toast Container */}
      <div className={`fixed z-50 ${positionClasses[position]} space-y-2`}>
        <AnimatePresence>
          {toasts.map((toast) => (
            <ToastComponent key={toast.id} toast={toast} onRemove={removeToast} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

// Individual Toast Component
interface ToastComponentProps {
  toast: Toast
  onRemove: (id: string) => void
}

const ToastComponent: React.FC<ToastComponentProps> = ({ toast, onRemove }) => {
  const icons = {
    success: CheckCircle,
    error: AlertTriangle,
    warning: AlertCircle,
    info: Info
  }

  const colors = {
    success: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-200 dark:border-green-800',
      icon: 'text-green-600 dark:text-green-400',
      text: 'text-green-800 dark:text-green-200'
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      icon: 'text-red-600 dark:text-red-400',
      text: 'text-red-800 dark:text-red-200'
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      icon: 'text-yellow-600 dark:text-yellow-400',
      text: 'text-yellow-800 dark:text-yellow-200'
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      icon: 'text-blue-600 dark:text-blue-400',
      text: 'text-blue-800 dark:text-blue-200'
    }
  }

  const Icon = icons[toast.type]
  const colorScheme = colors[toast.type]

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={`
        min-w-[320px] max-w-md p-4 rounded-lg border shadow-lg backdrop-blur-sm
        ${colorScheme.bg} ${colorScheme.border}
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${colorScheme.icon}`} />
        
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium ${colorScheme.text}`}>
            {toast.title}
          </h4>
          {toast.message && (
            <p className={`mt-1 text-sm ${colorScheme.text} opacity-80`}>
              {toast.message}
            </p>
          )}
          {toast.action && (
            <button
              onClick={toast.action.onClick}
              className={`mt-2 text-sm font-medium ${colorScheme.icon} hover:underline`}
            >
              {toast.action.label}
            </button>
          )}
        </div>

        <button
          onClick={() => onRemove(toast.id)}
          className={`flex-shrink-0 p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/10 ${colorScheme.text}`}
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}

// Error Boundary Component
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: any
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ error, errorInfo })
  }

  retry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return <FallbackComponent error={this.state.error!} retry={this.retry} />
      }
      return <DefaultErrorFallback error={this.state.error!} retry={this.retry} />
    }

    return this.props.children
  }
}

// Default Error Fallback
interface ErrorFallbackProps {
  error: Error
  retry: () => void
}

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ error, retry }) => (
  <div className="min-h-screen bg-synrgy-bg-950 flex items-center justify-center p-4">
    <div className="max-w-md w-full text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mb-6"
      >
        <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-synrgy-text mb-2">
          Something went wrong
        </h1>
        <p className="text-synrgy-muted mb-4">
          We encountered an unexpected error. Our team has been notified.
        </p>
        <details className="text-left bg-synrgy-surface p-4 rounded-lg mb-4 text-sm">
          <summary className="cursor-pointer text-synrgy-accent">
            Error Details
          </summary>
          <pre className="mt-2 text-synrgy-text whitespace-pre-wrap overflow-auto">
            {error.message}
          </pre>
        </details>
      </motion.div>
      
      <div className="space-y-3">
        <button
          onClick={retry}
          className="w-full px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors font-medium"
        >
          Try Again
        </button>
        <button
          onClick={() => window.location.reload()}
          className="w-full px-4 py-2 bg-synrgy-surface text-synrgy-text rounded-lg hover:bg-synrgy-surface/80 transition-colors"
        >
          Reload Page
        </button>
      </div>
    </div>
  </div>
)

// Empty State Component
interface EmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = AlertCircle,
  title,
  description,
  action,
  className = ''
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`text-center py-12 px-4 ${className}`}
  >
    <Icon className="w-12 h-12 text-synrgy-muted mx-auto mb-4" />
    <h3 className="text-lg font-medium text-synrgy-text mb-2">
      {title}
    </h3>
    {description && (
      <p className="text-synrgy-muted mb-6 max-w-sm mx-auto">
        {description}
      </p>
    )}
    {action && (
      <button
        onClick={action.onClick}
        className="px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors font-medium"
      >
        {action.label}
      </button>
    )}
  </motion.div>
)

// Loading State Component
interface LoadingStateProps {
  title?: string
  description?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  title = 'Loading...',
  description,
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: { container: 'py-8', spinner: 'w-6 h-6', title: 'text-base', desc: 'text-sm' },
    md: { container: 'py-12', spinner: 'w-8 h-8', title: 'text-lg', desc: 'text-base' },
    lg: { container: 'py-16', spinner: 'w-12 h-12', title: 'text-xl', desc: 'text-lg' }
  }

  const classes = sizeClasses[size]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`text-center ${classes.container} ${className}`}
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className={`${classes.spinner} border-2 border-synrgy-primary border-t-transparent rounded-full mx-auto mb-4`}
      />
      <h3 className={`font-medium text-synrgy-text mb-2 ${classes.title}`}>
        {title}
      </h3>
      {description && (
        <p className={`text-synrgy-muted ${classes.desc}`}>
          {description}
        </p>
      )}
    </motion.div>
  )
}

// Network Status Component
export const NetworkStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)
  const { showToast } = useToast()

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      showToast({
        type: 'success',
        title: 'Connection restored',
        message: 'You are back online'
      })
    }

    const handleOffline = () => {
      setIsOnline(false)
      showToast({
        type: 'error',
        title: 'Connection lost',
        message: 'Please check your internet connection'
      })
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [showToast])

  if (isOnline) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-2 text-center text-sm"
    >
      <div className="flex items-center justify-center gap-2">
        <WifiOff className="w-4 h-4" />
        <span>You are currently offline</span>
      </div>
    </motion.div>
  )
}

// Retry Component
interface RetryProps {
  onRetry: () => void
  loading?: boolean
  error?: string
  className?: string
}

export const Retry: React.FC<RetryProps> = ({
  onRetry,
  loading = false,
  error = 'Something went wrong',
  className = ''
}) => (
  <div className={`text-center py-8 ${className}`}>
    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-synrgy-text mb-2">
      {error}
    </h3>
    <button
      onClick={onRetry}
      disabled={loading}
      className="inline-flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors font-medium disabled:opacity-50"
    >
      <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
      {loading ? 'Retrying...' : 'Try Again'}
    </button>
  </div>
)

// Help Tooltip Component
interface HelpTooltipProps {
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  position = 'top',
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        className="p-1 text-synrgy-muted hover:text-synrgy-primary transition-colors"
        aria-label="Help information"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={`
              absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg
              whitespace-nowrap max-w-xs pointer-events-none
              ${position === 'top' ? 'bottom-full left-1/2 transform -translate-x-1/2 mb-2' : ''}
              ${position === 'bottom' ? 'top-full left-1/2 transform -translate-x-1/2 mt-2' : ''}
              ${position === 'left' ? 'right-full top-1/2 transform -translate-y-1/2 mr-2' : ''}
              ${position === 'right' ? 'left-full top-1/2 transform -translate-y-1/2 ml-2' : ''}
            `}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Quick Actions Floating Menu
interface QuickAction {
  icon: React.ComponentType<{ className?: string }>
  label: string
  onClick: () => void
  color?: string
}

interface QuickActionsProps {
  actions: QuickAction[]
  position?: 'bottom-right' | 'bottom-left'
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  actions,
  position = 'bottom-right'
}) => {
  const [isOpen, setIsOpen] = useState(false)

  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6'
  }

  return (
    <div className={`fixed z-40 ${positionClasses[position]}`}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="mb-4 space-y-2"
          >
            {actions.map((action, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => {
                  action.onClick()
                  setIsOpen(false)
                }}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-full shadow-lg
                  bg-synrgy-surface text-synrgy-text border border-synrgy-primary/20
                  hover:bg-synrgy-primary hover:text-synrgy-bg-900 transition-colors
                  backdrop-blur-sm
                `}
                title={action.label}
              >
                <action.icon className="w-5 h-5" />
                <span className="text-sm font-medium whitespace-nowrap">
                  {action.label}
                </span>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main FAB */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`
          w-14 h-14 rounded-full shadow-xl
          bg-gradient-to-r from-synrgy-primary to-synrgy-accent
          text-synrgy-bg-900 flex items-center justify-center
          hover:shadow-2xl transition-shadow
        `}
      >
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <Zap className="w-6 h-6" />
        </motion.div>
      </motion.button>
    </div>
  )
}
