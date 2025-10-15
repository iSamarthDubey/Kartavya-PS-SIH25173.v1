/**
 * SYNRGY Visual Polish & Theming
 * Advanced visual enhancements, gradients, shadows, and design tokens
 */

import React from 'react'
import { motion } from 'framer-motion'

// Design Tokens
export const designTokens = {
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },
  
  borderRadius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    '2xl': '1.5rem', // 24px
    full: '9999px'
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    glow: '0 0 20px rgba(0, 239, 255, 0.3)',
    'glow-accent': '0 0 20px rgba(255, 122, 0, 0.3)',
    'glow-soft': '0 0 40px rgba(0, 239, 255, 0.15)'
  },
  
  gradients: {
    primary: 'linear-gradient(135deg, #00EFFF 0%, #0EA5E9 100%)',
    accent: 'linear-gradient(135deg, #FF7A00 0%, #F97316 100%)',
    brand: 'linear-gradient(135deg, #00EFFF 0%, #FF7A00 100%)',
    surface: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%)',
    glass: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
    danger: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
    success: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    warning: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
  }
}

// Glass Effect Component
interface GlassProps {
  children: React.ReactNode
  className?: string
  intensity?: 'light' | 'medium' | 'strong'
}

export const Glass: React.FC<GlassProps> = ({ 
  children, 
  className = '', 
  intensity = 'medium' 
}) => {
  const intensityClasses = {
    light: 'bg-white/5 backdrop-blur-sm border-white/10',
    medium: 'bg-white/10 backdrop-blur-md border-white/20',
    strong: 'bg-white/20 backdrop-blur-lg border-white/30'
  }

  return (
    <div className={`${intensityClasses[intensity]} border rounded-xl ${className}`}>
      {children}
    </div>
  )
}

// Gradient Background Component
interface GradientBackgroundProps {
  variant?: keyof typeof designTokens.gradients
  className?: string
  animated?: boolean
  children?: React.ReactNode
}

export const GradientBackground: React.FC<GradientBackgroundProps> = ({
  variant = 'brand',
  className = '',
  animated = false,
  children
}) => {
  const gradient = designTokens.gradients[variant]

  return (
    <div 
      className={`relative overflow-hidden ${className}`}
      style={{ background: gradient }}
    >
      {animated && (
        <motion.div
          className="absolute inset-0 opacity-30"
          style={{
            background: 'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%)',
            backgroundSize: '200% 200%'
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%', '0% 0%']
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      )}
      {children}
    </div>
  )
}

// Animated Border Component
interface AnimatedBorderProps {
  children: React.ReactNode
  color?: string
  speed?: number
  className?: string
}

export const AnimatedBorder: React.FC<AnimatedBorderProps> = ({
  children,
  color = '#00EFFF',
  speed = 2,
  className = ''
}) => (
  <div className={`relative overflow-hidden rounded-xl ${className}`}>
    <motion.div
      className="absolute inset-0 opacity-75"
      style={{
        background: `conic-gradient(from 0deg, transparent, ${color}, transparent)`,
      }}
      animate={{ rotate: 360 }}
      transition={{ duration: speed, repeat: Infinity, ease: "linear" }}
    />
    <div className="relative bg-synrgy-bg-900 m-[1px] rounded-xl">
      {children}
    </div>
  </div>
)

// Enhanced Card with multiple visual effects
interface EnhancedCardProps {
  children: React.ReactNode
  variant?: 'default' | 'glass' | 'gradient' | 'glow'
  hoverable?: boolean
  className?: string
  onClick?: () => void
}

export const EnhancedCard: React.FC<EnhancedCardProps> = ({
  children,
  variant = 'default',
  hoverable = false,
  className = '',
  onClick
}) => {
  const variantClasses = {
    default: 'bg-synrgy-surface border border-synrgy-primary/20',
    glass: 'bg-white/10 backdrop-blur-md border border-white/20',
    gradient: 'bg-gradient-to-br from-synrgy-surface to-synrgy-bg-900',
    glow: 'bg-synrgy-surface border border-synrgy-primary/30 shadow-glow'
  }

  const hoverEffects = hoverable 
    ? {
        whileHover: { 
          y: -4, 
          scale: 1.02,
          boxShadow: variant === 'glow' 
            ? '0 0 30px rgba(0, 239, 255, 0.4)'
            : '0 20px 40px -10px rgba(0, 0, 0, 0.3)'
        },
        whileTap: { scale: 0.98 },
        transition: { type: "spring", stiffness: 300, damping: 20 }
      }
    : {}

  return (
    <motion.div
      className={`rounded-xl p-6 ${variantClasses[variant]} ${className} ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      {...hoverEffects}
    >
      {children}
    </motion.div>
  )
}

// Neon Text Effect
interface NeonTextProps {
  children: React.ReactNode
  color?: string
  intensity?: 'light' | 'medium' | 'strong'
  className?: string
}

export const NeonText: React.FC<NeonTextProps> = ({
  children,
  color = '#00EFFF',
  intensity = 'medium',
  className = ''
}) => {
  const intensityStyles = {
    light: { textShadow: `0 0 10px ${color}` },
    medium: { textShadow: `0 0 10px ${color}, 0 0 20px ${color}` },
    strong: { textShadow: `0 0 10px ${color}, 0 0 20px ${color}, 0 0 40px ${color}` }
  }

  return (
    <span 
      className={`text-transparent bg-clip-text ${className}`}
      style={{
        backgroundImage: `linear-gradient(45deg, ${color}, ${color}CC)`,
        ...intensityStyles[intensity]
      }}
    >
      {children}
    </span>
  )
}

// Particle Effect Background
interface ParticleBackgroundProps {
  particleCount?: number
  color?: string
  speed?: number
  size?: number
}

export const ParticleBackground: React.FC<ParticleBackgroundProps> = ({
  particleCount = 50,
  color = '#00EFFF',
  speed = 20,
  size = 2
}) => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {Array.from({ length: particleCount }, (_, i) => (
      <motion.div
        key={i}
        className="absolute rounded-full opacity-20"
        style={{
          backgroundColor: color,
          width: size,
          height: size,
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
        }}
        animate={{
          y: [0, -100, 0],
          opacity: [0.2, 0.8, 0.2],
        }}
        transition={{
          duration: speed + Math.random() * 10,
          repeat: Infinity,
          delay: Math.random() * 5,
          ease: "easeInOut"
        }}
      />
    ))}
  </div>
)

// Enhanced Button with multiple visual effects
interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'gradient' | 'neon'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ComponentType<{ className?: string }>
}

export const EnhancedButton: React.FC<EnhancedButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon: Icon,
  disabled,
  className = '',
  ...props
}) => {
  const baseClasses = "relative font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 overflow-hidden"
  
  const variantClasses = {
    primary: "bg-synrgy-primary text-synrgy-bg-900 hover:bg-synrgy-primary/90 focus:ring-synrgy-primary",
    secondary: "bg-synrgy-surface text-synrgy-text hover:bg-synrgy-surface/80 border border-synrgy-primary/20 focus:ring-synrgy-primary",
    ghost: "text-synrgy-primary hover:bg-synrgy-primary/10 focus:ring-synrgy-primary",
    gradient: "bg-gradient-to-r from-synrgy-primary to-synrgy-accent text-synrgy-bg-900 hover:shadow-lg focus:ring-synrgy-primary",
    neon: "bg-transparent border-2 border-synrgy-primary text-synrgy-primary hover:bg-synrgy-primary hover:text-synrgy-bg-900 focus:ring-synrgy-primary shadow-[0_0_20px_rgba(0,239,255,0.3)]"
  }
  
  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  }

  return (
    <motion.button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || loading}
      whileHover={!disabled && !loading ? { scale: 1.05 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.95 } : {}}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      {...props}
    >
      {/* Shine effect for gradient variant */}
      {variant === 'gradient' && (
        <motion.div
          className="absolute inset-0 -top-2 -left-2 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          style={{ transform: 'rotate(25deg)' }}
          initial={{ x: '-100%' }}
          whileHover={{ x: '200%' }}
          transition={{ duration: 0.6 }}
        />
      )}
      
      {/* Ripple effect */}
      <motion.div
        className="absolute inset-0 bg-white/20 rounded-xl"
        initial={{ scale: 0, opacity: 0 }}
        whileTap={{ scale: 4, opacity: 0.3 }}
        transition={{ duration: 0.3 }}
      />

      <div className="relative flex items-center justify-center gap-2">
        {loading ? (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
          />
        ) : Icon ? (
          <Icon className="w-4 h-4" />
        ) : null}
        {children}
      </div>
    </motion.button>
  )
}

// Floating Element with Physics
interface FloatingElementProps {
  children: React.ReactNode
  intensity?: 'subtle' | 'medium' | 'strong'
  className?: string
}

export const FloatingElement: React.FC<FloatingElementProps> = ({
  children,
  intensity = 'medium',
  className = ''
}) => {
  const intensityValues = {
    subtle: { y: [-2, 2], duration: 4 },
    medium: { y: [-5, 5], duration: 3 },
    strong: { y: [-10, 10], duration: 2 }
  }

  const config = intensityValues[intensity]

  return (
    <motion.div
      className={className}
      animate={{ y: config.y }}
      transition={{
        duration: config.duration,
        repeat: Infinity,
        repeatType: "reverse",
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  )
}

// Enhanced Grid with staggered animations
interface AnimatedGridProps {
  children: React.ReactNode
  columns?: number
  gap?: string
  staggerDelay?: number
  className?: string
}

export const AnimatedGrid: React.FC<AnimatedGridProps> = ({
  children,
  columns = 1,
  gap = '1rem',
  staggerDelay = 0.1,
  className = ''
}) => (
  <motion.div
    className={`grid ${className}`}
    style={{
      gridTemplateColumns: `repeat(${columns}, 1fr)`,
      gap
    }}
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
          hidden: { opacity: 0, y: 20, scale: 0.9 },
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

// Holographic Effect
interface HolographicProps {
  children: React.ReactNode
  className?: string
}

export const Holographic: React.FC<HolographicProps> = ({
  children,
  className = ''
}) => (
  <div className={`relative ${className}`}>
    <motion.div
      className="absolute inset-0 bg-gradient-to-r from-synrgy-primary via-synrgy-accent to-synrgy-primary opacity-20 blur-sm"
      animate={{
        background: [
          'linear-gradient(45deg, #00EFFF, #FF7A00, #00EFFF)',
          'linear-gradient(135deg, #FF7A00, #00EFFF, #FF7A00)',
          'linear-gradient(225deg, #00EFFF, #FF7A00, #00EFFF)',
          'linear-gradient(315deg, #FF7A00, #00EFFF, #FF7A00)'
        ]
      }}
      transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
    />
    <div className="relative">
      {children}
    </div>
  </div>
)

// Data Visualization Enhancement
interface DataVisualizationProps {
  value: number
  max?: number
  label?: string
  color?: string
  animated?: boolean
  showValue?: boolean
}

export const EnhancedProgressRing: React.FC<DataVisualizationProps> = ({
  value,
  max = 100,
  label,
  color = '#00EFFF',
  animated = true,
  showValue = true
}) => {
  const percentage = (value / max) * 100
  const circumference = 2 * Math.PI * 45
  const strokeDasharray = `${circumference} ${circumference}`
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        {/* Background ring */}
        <circle
          cx="50"
          cy="50"
          r="45"
          stroke="rgba(0, 239, 255, 0.1)"
          strokeWidth="8"
          fill="transparent"
        />
        
        {/* Progress ring */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          stroke={color}
          strokeWidth="8"
          fill="transparent"
          strokeLinecap="round"
          style={{
            strokeDasharray,
            strokeDashoffset: animated ? strokeDashoffset : 0
          }}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
        
        {/* Glow effect */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          stroke={color}
          strokeWidth="8"
          fill="transparent"
          strokeLinecap="round"
          className="opacity-50 blur-sm"
          style={{
            strokeDasharray,
            strokeDashoffset: animated ? strokeDashoffset : 0
          }}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          {showValue && (
            <motion.div
              className="text-2xl font-bold text-synrgy-text"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring" }}
            >
              {Math.round(percentage)}%
            </motion.div>
          )}
          {label && (
            <div className="text-xs text-synrgy-muted mt-1">
              {label}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
