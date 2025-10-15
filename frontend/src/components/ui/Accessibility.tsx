/**
 * SYNRGY Accessibility Components
 * Comprehensive a11y support for screen readers, keyboard navigation, and inclusive design
 */

import React, { useEffect, useRef, createContext, useContext } from 'react'
import { motion } from 'framer-motion'

// Accessibility Context
interface A11yContextType {
  announceToScreenReader: (message: string, priority?: 'polite' | 'assertive') => void
  focusElement: (selector: string) => void
  isReducedMotion: boolean
}

const A11yContext = createContext<A11yContextType | undefined>(undefined)

export const useA11y = () => {
  const context = useContext(A11yContext)
  if (!context) {
    throw new Error('useA11y must be used within an A11yProvider')
  }
  return context
}

// Screen Reader Announcer
export const ScreenReaderAnnouncer: React.FC = () => (
  <div
    id="screen-reader-announcer"
    aria-live="polite"
    aria-atomic="true"
    className="sr-only"
  />
)

export const ScreenReaderAssertive: React.FC = () => (
  <div
    id="screen-reader-assertive"
    aria-live="assertive"
    aria-atomic="true"
    className="sr-only"
  />
)

// Skip Links
export const SkipLinks: React.FC = () => (
  <div className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50">
    <a
      href="#main-content"
      className="bg-synrgy-primary text-synrgy-bg-900 px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:ring-offset-2"
    >
      Skip to main content
    </a>
    <a
      href="#navigation"
      className="ml-2 bg-synrgy-primary text-synrgy-bg-900 px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:ring-offset-2"
    >
      Skip to navigation
    </a>
  </div>
)

// Accessibility Provider
interface A11yProviderProps {
  children: React.ReactNode
}

export const A11yProvider: React.FC<A11yProviderProps> = ({ children }) => {
  const isReducedMotion = typeof window !== 'undefined' 
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false

  const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcerId = priority === 'assertive' ? 'screen-reader-assertive' : 'screen-reader-announcer'
    const announcer = document.getElementById(announcerId)
    if (announcer) {
      announcer.textContent = message
      // Clear after announcement
      setTimeout(() => {
        announcer.textContent = ''
      }, 1000)
    }
  }

  const focusElement = (selector: string) => {
    const element = document.querySelector(selector) as HTMLElement
    if (element) {
      element.focus()
    }
  }

  return (
    <A11yContext.Provider value={{ announceToScreenReader, focusElement, isReducedMotion }}>
      <SkipLinks />
      <ScreenReaderAnnouncer />
      <ScreenReaderAssertive />
      {children}
    </A11yContext.Provider>
  )
}

// Accessible Button with proper ARIA attributes
interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  description?: string
  shortcut?: string
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  description,
  shortcut,
  disabled,
  className = '',
  onClick,
  ...props
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const { announceToScreenReader, isReducedMotion } = useA11y()

  const baseClasses = "font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 relative overflow-hidden"
  
  const variantClasses = {
    primary: "bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 focus:ring-synrgy-primary",
    secondary: "bg-synrgy-surface text-synrgy-text hover:bg-synrgy-surface/80 focus:ring-synrgy-primary border border-synrgy-primary/20",
    ghost: "text-synrgy-primary hover:bg-synrgy-primary/10 focus:ring-synrgy-primary",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  }
  
  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  }

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (loading || disabled) return
    
    // Announce action for screen readers
    if (description) {
      announceToScreenReader(description)
    }
    
    onClick?.(e)
  }

  // Keyboard shortcut handler
  useEffect(() => {
    if (!shortcut) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === shortcut && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        buttonRef.current?.click()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [shortcut])

  return (
    <motion.button
      ref={buttonRef}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || loading}
      onClick={handleClick}
      aria-describedby={description ? `${props.id}-description` : undefined}
      aria-keyshortcuts={shortcut}
      whileHover={!isReducedMotion && !disabled && !loading ? { scale: 1.02 } : {}}
      whileTap={!isReducedMotion && !disabled && !loading ? { scale: 0.98 } : {}}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
            aria-hidden="true"
          />
        </div>
      )}
      <span className={loading ? 'opacity-0' : 'opacity-100'}>
        {children}
      </span>
      {description && (
        <div id={`${props.id}-description`} className="sr-only">
          {description}
        </div>
      )}
    </motion.button>
  )
}

// Accessible Input with proper labels and validation
interface AccessibleInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  hint?: string
  required?: boolean
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  label,
  error,
  hint,
  required = false,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
  const errorId = `${inputId}-error`
  const hintId = `${inputId}-hint`

  return (
    <div className={`space-y-2 ${className}`}>
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-synrgy-text"
      >
        {label}
        {required && (
          <span className="text-red-400 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      
      {hint && (
        <p id={hintId} className="text-sm text-synrgy-muted">
          {hint}
        </p>
      )}
      
      <input
        id={inputId}
        className={`
          w-full px-3 py-2 bg-synrgy-surface border rounded-lg
          text-synrgy-text placeholder:text-synrgy-muted
          focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:border-transparent
          ${error 
            ? 'border-red-500 focus:ring-red-500' 
            : 'border-synrgy-primary/20 hover:border-synrgy-primary/40'
          }
        `}
        aria-describedby={`${error ? errorId : ''} ${hint ? hintId : ''}`.trim()}
        aria-invalid={error ? 'true' : 'false'}
        aria-required={required}
        {...props}
      />
      
      {error && (
        <p id={errorId} className="text-sm text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

// Accessible Modal with focus management
interface AccessibleModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md'
}) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const { announceToScreenReader } = useA11y()

  // Focus management
  useEffect(() => {
    if (!isOpen) return

    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    const firstElement = focusableElements?.[0] as HTMLElement
    const lastElement = focusableElements?.[focusableElements.length - 1] as HTMLElement

    // Focus first element
    firstElement?.focus()

    // Announce modal opened
    announceToScreenReader(`${title} dialog opened`, 'assertive')

    // Trap focus
    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus()
          e.preventDefault()
        }
      }
    }

    // Handle escape key
    const handleEscapeKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleTabKey)
    document.addEventListener('keydown', handleEscapeKey)

    return () => {
      document.removeEventListener('keydown', handleTabKey)
      document.removeEventListener('keydown', handleEscapeKey)
      announceToScreenReader(`${title} dialog closed`, 'assertive')
    }
  }, [isOpen, title, onClose, announceToScreenReader])

  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl'
  }

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="flex min-h-screen items-center justify-center p-4">
        <div
          ref={modalRef}
          className={`
            relative w-full ${sizeClasses[size]} max-h-[90vh] overflow-auto
            bg-synrgy-surface border border-synrgy-primary/20 rounded-2xl shadow-2xl
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10">
            <h2 id="modal-title" className="text-xl font-semibold text-synrgy-text">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-synrgy-primary"
              aria-label="Close dialog"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

// Accessible Progress Bar
interface AccessibleProgressProps {
  value: number
  max?: number
  label: string
  showValue?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export const AccessibleProgress: React.FC<AccessibleProgressProps> = ({
  value,
  max = 100,
  label,
  showValue = true,
  size = 'md'
}) => {
  const percentage = Math.round((value / max) * 100)
  
  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-synrgy-text">
          {label}
        </span>
        {showValue && (
          <span className="text-sm text-synrgy-muted" aria-hidden="true">
            {percentage}%
          </span>
        )}
      </div>
      
      <div
        className={`w-full bg-synrgy-surface rounded-full overflow-hidden ${sizeClasses[size]}`}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={`${label}: ${percentage}% complete`}
      >
        <motion.div
          className="h-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  )
}

// Accessible Tooltip
interface AccessibleTooltipProps {
  children: React.ReactNode
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export const AccessibleTooltip: React.FC<AccessibleTooltipProps> = ({
  children,
  content,
  position = 'top'
}) => {
  const [isVisible, setIsVisible] = React.useState(false)
  const tooltipId = `tooltip-${Math.random().toString(36).substr(2, 9)}`

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      <div aria-describedby={tooltipId}>
        {children}
      </div>
      
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className={`
            absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded-lg
            whitespace-nowrap pointer-events-none
            ${positionClasses[position]}
          `}
        >
          {content}
          {/* Arrow */}
          <div
            className={`
              absolute w-2 h-2 bg-gray-900 rotate-45
              ${position === 'top' ? 'top-full left-1/2 transform -translate-x-1/2 -translate-y-1/2' : ''}
              ${position === 'bottom' ? 'bottom-full left-1/2 transform -translate-x-1/2 translate-y-1/2' : ''}
              ${position === 'left' ? 'left-full top-1/2 transform -translate-x-1/2 -translate-y-1/2' : ''}
              ${position === 'right' ? 'right-full top-1/2 transform translate-x-1/2 -translate-y-1/2' : ''}
            `}
          />
        </div>
      )}
    </div>
  )
}

// Keyboard Navigation Helper
export const useKeyboardNavigation = (
  items: string[],
  onSelect: (item: string) => void,
  enabled = true
) => {
  const [focusedIndex, setFocusedIndex] = React.useState(0)

  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusedIndex((prev) => (prev + 1) % items.length)
          break
        case 'ArrowUp':
          e.preventDefault()
          setFocusedIndex((prev) => (prev - 1 + items.length) % items.length)
          break
        case 'Enter':
        case ' ':
          e.preventDefault()
          onSelect(items[focusedIndex])
          break
        case 'Escape':
          setFocusedIndex(0)
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [items, focusedIndex, onSelect, enabled])

  return focusedIndex
}
