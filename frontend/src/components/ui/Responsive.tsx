/**
 * SYNRGY Responsive Design Components
 * Mobile-first design with touch interactions and adaptive layouts
 */

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, ChevronDown, ChevronRight } from 'lucide-react'

// Breakpoint utilities
export const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
} as const

type Breakpoint = keyof typeof breakpoints

// Custom hook for responsive design
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('lg')

  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth
      
      if (width >= breakpoints['2xl']) {
        setBreakpoint('2xl')
      } else if (width >= breakpoints.xl) {
        setBreakpoint('xl')
      } else if (width >= breakpoints.lg) {
        setBreakpoint('lg')
      } else if (width >= breakpoints.md) {
        setBreakpoint('md')
      } else {
        setBreakpoint('sm')
      }
    }

    updateBreakpoint()
    window.addEventListener('resize', updateBreakpoint)
    return () => window.removeEventListener('resize', updateBreakpoint)
  }, [])

  const isMobile = breakpoint === 'sm'
  const isTablet = breakpoint === 'md'
  const isDesktop = ['lg', 'xl', '2xl'].includes(breakpoint)

  return { breakpoint, isMobile, isTablet, isDesktop }
}

// Responsive Container
interface ResponsiveContainerProps {
  children: React.ReactNode
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
  padding?: boolean
  className?: string
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  maxWidth = 'xl',
  padding = true,
  className = ''
}) => {
  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-7xl',
    '2xl': 'max-w-full',
    full: 'w-full'
  }

  const paddingClasses = padding ? 'px-4 sm:px-6 lg:px-8' : ''

  return (
    <div className={`mx-auto ${maxWidthClasses[maxWidth]} ${paddingClasses} ${className}`}>
      {children}
    </div>
  )
}

// Responsive Grid
interface ResponsiveGridProps {
  children: React.ReactNode
  columns?: {
    sm?: number
    md?: number
    lg?: number
    xl?: number
  }
  gap?: number
  className?: string
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  columns = { sm: 1, md: 2, lg: 3, xl: 4 },
  gap = 6,
  className = ''
}) => {
  const gridClasses = [
    `grid gap-${gap}`,
    columns.sm && `grid-cols-${columns.sm}`,
    columns.md && `md:grid-cols-${columns.md}`,
    columns.lg && `lg:grid-cols-${columns.lg}`,
    columns.xl && `xl:grid-cols-${columns.xl}`
  ].filter(Boolean).join(' ')

  return (
    <div className={`${gridClasses} ${className}`}>
      {children}
    </div>
  )
}

// Mobile Navigation Drawer
interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  title?: string
}

export const MobileDrawer: React.FC<MobileDrawerProps> = ({
  isOpen,
  onClose,
  children,
  title
}) => (
  <AnimatePresence>
    {isOpen && (
      <>
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
        />

        {/* Drawer */}
        <motion.div
          initial={{ x: '-100%' }}
          animate={{ x: 0 }}
          exit={{ x: '-100%' }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="fixed top-0 left-0 h-full w-80 max-w-[85vw] bg-synrgy-surface border-r border-synrgy-primary/20 z-50 lg:hidden"
        >
          {/* Header */}
          {title && (
            <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10">
              <h2 className="text-xl font-semibold text-synrgy-text">
                {title}
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-synrgy-text" />
              </button>
            </div>
          )}

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {children}
          </div>
        </motion.div>
      </>
    )}
  </AnimatePresence>
)

// Touch-Optimized Button
interface TouchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

export const TouchButton: React.FC<TouchButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  ...props
}) => {
  const { isMobile } = useBreakpoint()

  const baseClasses = "font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 active:scale-95"
  
  const variantClasses = {
    primary: "bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 focus:ring-synrgy-primary",
    secondary: "bg-synrgy-surface text-synrgy-text hover:bg-synrgy-surface/80 border border-synrgy-primary/20 focus:ring-synrgy-primary",
    ghost: "text-synrgy-primary hover:bg-synrgy-primary/10 focus:ring-synrgy-primary"
  }
  
  // Larger touch targets on mobile
  const sizeClasses = {
    sm: isMobile ? "px-6 py-3 text-base min-h-[44px]" : "px-4 py-2 text-sm",
    md: isMobile ? "px-8 py-4 text-lg min-h-[48px]" : "px-6 py-3 text-base",
    lg: isMobile ? "px-10 py-5 text-xl min-h-[52px]" : "px-8 py-4 text-lg"
  }

  const widthClass = fullWidth ? 'w-full' : ''

  return (
    <motion.button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      {...props}
    >
      {children}
    </motion.button>
  )
}

// Responsive Modal
interface ResponsiveModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

export const ResponsiveModal: React.FC<ResponsiveModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md'
}) => {
  const { isMobile } = useBreakpoint()

  const sizeClasses = isMobile 
    ? 'w-full h-full max-w-none max-h-none rounded-none'
    : {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-xl',
        full: 'max-w-4xl'
      }[size]

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <div className="flex min-h-screen items-center justify-center p-4">
            <motion.div
              initial={isMobile ? { y: '100%' } : { opacity: 0, scale: 0.8 }}
              animate={isMobile ? { y: 0 } : { opacity: 1, scale: 1 }}
              exit={isMobile ? { y: '100%' } : { opacity: 0, scale: 0.8 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
              className={`
                relative w-full bg-synrgy-surface border border-synrgy-primary/20 
                shadow-2xl overflow-hidden
                ${isMobile ? 'h-full flex flex-col' : `${sizeClasses} max-h-[90vh] rounded-2xl`}
              `}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-synrgy-primary/10 flex-shrink-0">
                <h2 className="text-xl font-semibold text-synrgy-text">
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-synrgy-text" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {children}
              </div>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  )
}

// Responsive Tabs
interface ResponsiveTabsProps {
  tabs: Array<{
    id: string
    label: string
    content: React.ReactNode
  }>
  activeTab?: string
  onTabChange?: (tabId: string) => void
}

export const ResponsiveTabs: React.FC<ResponsiveTabsProps> = ({
  tabs,
  activeTab,
  onTabChange
}) => {
  const { isMobile } = useBreakpoint()
  const [currentTab, setCurrentTab] = useState(activeTab || tabs[0]?.id)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const handleTabChange = (tabId: string) => {
    setCurrentTab(tabId)
    onTabChange?.(tabId)
    setIsDropdownOpen(false)
  }

  const currentTabData = tabs.find(tab => tab.id === currentTab)

  if (isMobile) {
    // Mobile: Dropdown-style tabs
    return (
      <div className="w-full">
        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full flex items-center justify-between p-4 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl text-synrgy-text"
          >
            <span>{currentTabData?.label}</span>
            <ChevronDown className={`w-5 h-5 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-2 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-lg z-10"
              >
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={`
                      w-full px-4 py-3 text-left hover:bg-synrgy-primary/10 transition-colors first:rounded-t-xl last:rounded-b-xl
                      ${currentTab === tab.id ? 'bg-synrgy-primary/20 text-synrgy-primary' : 'text-synrgy-text'}
                    `}
                  >
                    {tab.label}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="mt-6">
          {currentTabData?.content}
        </div>
      </div>
    )
  }

  // Desktop: Traditional tabs
  return (
    <div className="w-full">
      <div className="border-b border-synrgy-primary/10">
        <nav className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`
                px-6 py-3 text-sm font-medium rounded-t-lg transition-colors
                ${currentTab === tab.id
                  ? 'border-b-2 border-synrgy-primary text-synrgy-primary bg-synrgy-primary/5'
                  : 'text-synrgy-muted hover:text-synrgy-text hover:bg-synrgy-primary/5'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {currentTabData?.content}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}

// Responsive Card Stack (Mobile Carousel, Desktop Grid)
interface ResponsiveCardStackProps {
  children: React.ReactNode[]
  spacing?: number
}

export const ResponsiveCardStack: React.FC<ResponsiveCardStackProps> = ({
  children,
  spacing = 4
}) => {
  const { isMobile, isTablet } = useBreakpoint()
  const [currentIndex, setCurrentIndex] = useState(0)

  if (isMobile) {
    // Mobile: Swipeable carousel
    return (
      <div className="w-full">
        <div className="overflow-hidden">
          <motion.div
            className="flex"
            animate={{ x: `-${currentIndex * 100}%` }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            {children.map((child, index) => (
              <div
                key={index}
                className="w-full flex-shrink-0 px-4"
              >
                {child}
              </div>
            ))}
          </motion.div>
        </div>

        {/* Dots indicator */}
        <div className="flex justify-center mt-4 space-x-2">
          {children.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`
                w-2 h-2 rounded-full transition-colors
                ${currentIndex === index ? 'bg-synrgy-primary' : 'bg-synrgy-primary/30'}
              `}
            />
          ))}
        </div>
      </div>
    )
  }

  // Desktop/Tablet: Grid layout
  const columns = isTablet ? 2 : 3
  
  return (
    <div className={`grid grid-cols-1 md:grid-cols-${columns} gap-${spacing}`}>
      {children}
    </div>
  )
}

// Responsive Text
interface ResponsiveTextProps {
  children: React.ReactNode
  size?: {
    sm?: string
    md?: string
    lg?: string
  }
  className?: string
}

export const ResponsiveText: React.FC<ResponsiveTextProps> = ({
  children,
  size = { sm: 'text-sm', md: 'text-base', lg: 'text-lg' },
  className = ''
}) => {
  const responsiveClasses = [
    size.sm,
    size.md && `md:${size.md}`,
    size.lg && `lg:${size.lg}`
  ].filter(Boolean).join(' ')

  return (
    <span className={`${responsiveClasses} ${className}`}>
      {children}
    </span>
  )
}

// Touch-optimized Input
interface TouchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ComponentType<{ className?: string }>
}

export const TouchInput: React.FC<TouchInputProps> = ({
  label,
  error,
  icon: Icon,
  className = '',
  ...props
}) => {
  const { isMobile } = useBreakpoint()
  
  // Larger touch targets on mobile
  const inputHeight = isMobile ? 'h-12' : 'h-10'
  const paddingX = isMobile ? 'px-4' : 'px-3'

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-synrgy-text mb-2">
          {label}
        </label>
      )}
      
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-synrgy-muted" />
        )}
        
        <input
          className={`
            w-full ${inputHeight} ${paddingX} ${Icon ? 'pl-10' : ''} 
            bg-synrgy-surface border border-synrgy-primary/20 rounded-xl
            text-synrgy-text placeholder:text-synrgy-muted
            focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:border-transparent
            ${error ? 'border-red-500 focus:ring-red-500' : 'hover:border-synrgy-primary/40'}
            ${className}
          `}
          {...props}
        />
      </div>
      
      {error && (
        <p className="mt-2 text-sm text-red-400">
          {error}
        </p>
      )}
    </div>
  )
}

// Responsive Spacing
export const spacing = {
  xs: { mobile: 'space-y-2', desktop: 'space-y-2' },
  sm: { mobile: 'space-y-3', desktop: 'space-y-4' },
  md: { mobile: 'space-y-4', desktop: 'space-y-6' },
  lg: { mobile: 'space-y-6', desktop: 'space-y-8' },
  xl: { mobile: 'space-y-8', desktop: 'space-y-12' }
} as const

interface ResponsiveSpaceProps {
  children: React.ReactNode
  size?: keyof typeof spacing
  direction?: 'vertical' | 'horizontal'
  className?: string
}

export const ResponsiveSpace: React.FC<ResponsiveSpaceProps> = ({
  children,
  size = 'md',
  direction = 'vertical',
  className = ''
}) => {
  const { isMobile } = useBreakpoint()
  const spaceClass = isMobile ? spacing[size].mobile : spacing[size].desktop
  const directionClass = direction === 'horizontal' 
    ? spaceClass.replace('space-y', 'space-x')
    : spaceClass

  return (
    <div className={`${directionClass} ${className}`}>
      {children}
    </div>
  )
}
