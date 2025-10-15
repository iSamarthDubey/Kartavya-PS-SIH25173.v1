/**
 * SYNRGY Advanced Animation System
 * Smooth transitions and micro-interactions for premium UX
 */

import React, { forwardRef } from 'react'
import { motion, AnimatePresence, Variants, HTMLMotionProps } from 'framer-motion'

// Animation variants
export const pageVariants: Variants = {
  initial: { 
    opacity: 0, 
    x: -20,
    scale: 0.98
  },
  in: { 
    opacity: 1, 
    x: 0,
    scale: 1
  },
  out: { 
    opacity: 0, 
    x: 20,
    scale: 0.98
  }
}

export const slideVariants: Variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 1000 : -1000,
    opacity: 0
  }),
  center: {
    zIndex: 1,
    x: 0,
    opacity: 1
  },
  exit: (direction: number) => ({
    zIndex: 0,
    x: direction < 0 ? 1000 : -1000,
    opacity: 0
  })
}

export const cardVariants: Variants = {
  initial: { 
    opacity: 0, 
    y: 20,
    scale: 0.95
  },
  animate: { 
    opacity: 1, 
    y: 0,
    scale: 1
  },
  hover: {
    y: -4,
    scale: 1.02,
    boxShadow: "0 25px 50px -12px rgba(0, 239, 255, 0.15)",
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 20
    }
  },
  tap: {
    scale: 0.98,
    transition: { duration: 0.1 }
  }
}

export const buttonVariants: Variants = {
  initial: { scale: 1 },
  hover: { 
    scale: 1.05,
    boxShadow: "0 10px 25px -5px rgba(0, 239, 255, 0.2)",
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 15
    }
  },
  tap: { 
    scale: 0.95,
    transition: { duration: 0.1 }
  },
  disabled: { 
    scale: 1, 
    opacity: 0.6,
    transition: { duration: 0.2 }
  }
}

export const modalVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
    y: 50
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 25,
      duration: 0.3
    }
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    y: 50,
    transition: {
      duration: 0.2
    }
  }
}

export const listVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.1,
      staggerChildren: 0.05
    }
  }
}

export const listItemVariants: Variants = {
  hidden: { 
    opacity: 0, 
    y: 10,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 30
    }
  }
}

// Enhanced Components
interface AnimatedPageProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode
  className?: string
}

export const AnimatedPage = forwardRef<HTMLDivElement, AnimatedPageProps>(
  ({ children, className = "", ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={{
        type: "tween",
        ease: "easeInOut",
        duration: 0.4
      }}
      className={`w-full ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  )
)
AnimatedPage.displayName = 'AnimatedPage'

export const AnimatedCard = forwardRef<HTMLDivElement, AnimatedPageProps>(
  ({ children, className = "", ...props }, ref) => (
    <motion.div
      ref={ref}
      variants={cardVariants}
      initial="initial"
      animate="animate"
      whileHover="hover"
      whileTap="tap"
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
)
AnimatedCard.displayName = 'AnimatedCard'

interface AnimatedButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'ghost'
}

export const AnimatedButton = forwardRef<HTMLButtonElement, AnimatedButtonProps>(
  ({ children, disabled = false, variant = 'primary', className = "", ...props }, ref) => {
    const baseClasses = "px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
    const variantClasses = {
      primary: "bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 focus:ring-synrgy-primary",
      secondary: "bg-synrgy-surface text-synrgy-text hover:bg-synrgy-surface/80 focus:ring-synrgy-primary",
      ghost: "text-synrgy-primary hover:bg-synrgy-primary/10 focus:ring-synrgy-primary"
    }
    
    return (
      <motion.button
        ref={ref}
        variants={buttonVariants}
        initial="initial"
        whileHover={disabled ? "disabled" : "hover"}
        whileTap={disabled ? "disabled" : "tap"}
        animate={disabled ? "disabled" : "initial"}
        disabled={disabled}
        className={`${baseClasses} ${variantClasses[variant]} ${className}`}
        {...props}
      >
        {children}
      </motion.button>
    )
  }
)
AnimatedButton.displayName = 'AnimatedButton'

export const AnimatedList = forwardRef<HTMLDivElement, AnimatedPageProps>(
  ({ children, className = "", ...props }, ref) => (
    <motion.div
      ref={ref}
      variants={listVariants}
      initial="hidden"
      animate="visible"
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
)
AnimatedList.displayName = 'AnimatedList'

export const AnimatedListItem = forwardRef<HTMLDivElement, AnimatedPageProps>(
  ({ children, className = "", ...props }, ref) => (
    <motion.div
      ref={ref}
      variants={listItemVariants}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
)
AnimatedListItem.displayName = 'AnimatedListItem'

// Modal with backdrop
interface AnimatedModalProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  className?: string
}

export const AnimatedModal: React.FC<AnimatedModalProps> = ({
  isOpen,
  onClose,
  children,
  className = ""
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
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        />
        
        {/* Modal */}
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={`bg-synrgy-surface border border-synrgy-primary/20 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-auto ${className}`}
            onClick={(e) => e.stopPropagation()}
          >
            {children}
          </motion.div>
        </div>
      </>
    )}
  </AnimatePresence>
)

// Staggered grid animation
interface StaggeredGridProps {
  children: React.ReactNode
  className?: string
  staggerDelay?: number
}

export const StaggeredGrid: React.FC<StaggeredGridProps> = ({
  children,
  className = "",
  staggerDelay = 0.1
}) => (
  <motion.div
    className={className}
    initial="hidden"
    animate="visible"
    variants={{
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: staggerDelay
        }
      }
    }}
  >
    {React.Children.map(children, (child, index) => (
      <motion.div
        key={index}
        variants={{
          hidden: { opacity: 0, y: 20, scale: 0.95 },
          visible: { 
            opacity: 1, 
            y: 0, 
            scale: 1,
            transition: {
              type: "spring",
              stiffness: 400,
              damping: 25
            }
          }
        }}
      >
        {child}
      </motion.div>
    ))}
  </motion.div>
)

// Floating action button with ripple effect
interface FloatingButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg'
}

export const FloatingButton = forwardRef<HTMLButtonElement, FloatingButtonProps>(
  ({ children, size = 'md', className = "", ...props }, ref) => {
    const sizeClasses = {
      sm: "w-10 h-10",
      md: "w-12 h-12", 
      lg: "w-16 h-16"
    }

    return (
      <motion.button
        ref={ref}
        className={`
          ${sizeClasses[size]}
          bg-gradient-to-r from-synrgy-primary to-synrgy-accent
          text-synrgy-bg-900 rounded-full shadow-lg
          flex items-center justify-center
          focus:outline-none focus:ring-4 focus:ring-synrgy-primary/30
          overflow-hidden relative
          ${className}
        `}
        whileHover={{ 
          scale: 1.1,
          boxShadow: "0 20px 40px -10px rgba(0, 239, 255, 0.3)"
        }}
        whileTap={{ scale: 0.9 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{
          type: "spring",
          stiffness: 260,
          damping: 20
        }}
        {...props}
      >
        <motion.div
          className="absolute inset-0 bg-white/20 rounded-full"
          initial={{ scale: 0, opacity: 0 }}
          whileTap={{ scale: 4, opacity: 0.3 }}
          transition={{ duration: 0.3 }}
        />
        {children}
      </motion.button>
    )
  }
)
FloatingButton.displayName = 'FloatingButton'

// Page transition wrapper
interface PageTransitionProps {
  children: React.ReactNode
  location: string
}

export const PageTransition: React.FC<PageTransitionProps> = ({ 
  children, 
  location 
}) => (
  <AnimatePresence mode="wait" initial={false}>
    <motion.div
      key={location}
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={{
        type: "tween",
        ease: "easeInOut",
        duration: 0.4
      }}
    >
      {children}
    </motion.div>
  </AnimatePresence>
)

// Spotlight effect for important elements
interface SpotlightProps {
  children: React.ReactNode
  intensity?: 'low' | 'medium' | 'high'
  color?: 'primary' | 'accent' | 'success' | 'warning' | 'error'
}

export const Spotlight: React.FC<SpotlightProps> = ({
  children,
  intensity = 'medium',
  color = 'primary'
}) => {
  const intensityClasses = {
    low: 'shadow-lg',
    medium: 'shadow-xl',
    high: 'shadow-2xl'
  }

  const colorClasses = {
    primary: 'shadow-synrgy-primary/20',
    accent: 'shadow-synrgy-accent/20',
    success: 'shadow-green-500/20',
    warning: 'shadow-yellow-500/20',
    error: 'shadow-red-500/20'
  }

  return (
    <motion.div
      className={`relative ${intensityClasses[intensity]} ${colorClasses[color]}`}
      whileHover={{
        scale: 1.02,
        boxShadow: intensity === 'high' 
          ? "0 25px 50px -12px rgba(0, 239, 255, 0.25)"
          : "0 20px 40px -10px rgba(0, 239, 255, 0.2)"
      }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 20
      }}
    >
      {children}
      
      {/* Animated border gradient */}
      <motion.div
        className="absolute inset-0 rounded-inherit opacity-0 pointer-events-none"
        style={{
          background: `linear-gradient(45deg, 
            transparent 30%, 
            rgba(0, 239, 255, 0.1) 50%, 
            transparent 70%
          )`,
          backgroundSize: '200% 200%'
        }}
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%']
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          repeatType: 'reverse'
        }}
        whileHover={{
          opacity: 1
        }}
      />
    </motion.div>
  )
}
