/**
 * SYNRGY Skeleton Loading Components
 * Sophisticated loading states for better perceived performance
 */

import React from 'react'
import { motion } from 'framer-motion'

interface SkeletonProps {
  className?: string
  width?: string | number
  height?: string | number
  rounded?: boolean
  pulse?: boolean
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  width = '100%',
  height = '1rem',
  rounded = false,
  pulse = true
}) => {
  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  }

  return (
    <div
      className={`bg-gradient-to-r from-synrgy-surface to-synrgy-surface/50 ${
        rounded ? 'rounded-full' : 'rounded-lg'
      } ${pulse ? 'animate-pulse' : ''} ${className}`}
      style={style}
    />
  )
}

// Chart Skeleton
export const ChartSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-6 ${className}`}>
    <div className="flex items-center justify-between mb-4">
      <Skeleton width="40%" height="1.5rem" />
      <div className="flex gap-2">
        <Skeleton width="2rem" height="2rem" rounded />
        <Skeleton width="2rem" height="2rem" rounded />
      </div>
    </div>
    
    {/* Chart area */}
    <div className="relative h-64 mb-4">
      <div className="absolute inset-0 flex items-end justify-around gap-2">
        {Array.from({ length: 8 }, (_, i) => (
          <motion.div
            key={i}
            initial={{ height: 0 }}
            animate={{ height: `${Math.random() * 80 + 20}%` }}
            transition={{ delay: i * 0.1, duration: 0.6, ease: "easeOut" }}
            className="bg-gradient-to-t from-synrgy-primary/30 to-synrgy-primary/10 rounded-t-lg flex-1"
          />
        ))}
      </div>
    </div>
    
    {/* Legend */}
    <div className="flex gap-4">
      <Skeleton width="20%" height="0.75rem" />
      <Skeleton width="15%" height="0.75rem" />
      <Skeleton width="25%" height="0.75rem" />
    </div>
  </div>
)

// Table Skeleton
export const TableSkeleton: React.FC<{ rows?: number; columns?: number; className?: string }> = ({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) => (
  <div className={`bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl overflow-hidden ${className}`}>
    {/* Header */}
    <div className="bg-synrgy-bg-900/50 p-4 border-b border-synrgy-primary/10">
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }, (_, i) => (
          <Skeleton key={i} width="80%" height="1rem" />
        ))}
      </div>
    </div>
    
    {/* Rows */}
    <div className="p-4 space-y-3">
      {Array.from({ length: rows }, (_, rowIndex) => (
        <motion.div
          key={rowIndex}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: rowIndex * 0.05, duration: 0.4 }}
          className="grid gap-4"
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }, (_, colIndex) => (
            <Skeleton 
              key={colIndex} 
              width={`${Math.random() * 30 + 60}%`} 
              height="0.875rem" 
            />
          ))}
        </motion.div>
      ))}
    </div>
  </div>
)

// Card Skeleton
export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-6 ${className}`}>
    <div className="flex items-center justify-between mb-4">
      <Skeleton width="60%" height="1.25rem" />
      <Skeleton width="2rem" height="2rem" rounded />
    </div>
    
    <div className="space-y-3">
      <Skeleton width="100%" height="3rem" />
      <div className="flex justify-between">
        <Skeleton width="40%" height="0.875rem" />
        <Skeleton width="30%" height="0.875rem" />
      </div>
    </div>
  </div>
)

// Dashboard Grid Skeleton
export const DashboardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`space-y-8 ${className}`}>
    {/* Header */}
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton width="20rem" height="2.5rem" />
        <Skeleton width="30rem" height="1.25rem" />
      </div>
      <div className="flex gap-3">
        <Skeleton width="3rem" height="3rem" rounded />
        <Skeleton width="3rem" height="3rem" rounded />
      </div>
    </div>

    {/* Summary Cards */}
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
      {Array.from({ length: 4 }, (_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.4 }}
        >
          <CardSkeleton />
        </motion.div>
      ))}
    </div>

    {/* Charts */}
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div className="xl:col-span-2">
        <ChartSkeleton />
      </div>
      <div className="xl:col-span-1">
        <ChartSkeleton />
      </div>
    </div>

    {/* Table */}
    <TableSkeleton />
  </div>
)

// Chat Message Skeleton
export const ChatMessageSkeleton: React.FC<{ className?: string; isUser?: boolean }> = ({ 
  className = '', 
  isUser = false 
}) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`flex gap-4 p-4 ${isUser ? 'justify-end' : 'justify-start'} ${className}`}
  >
    {!isUser && (
      <div className="flex-shrink-0">
        <Skeleton width="2.5rem" height="2.5rem" rounded />
      </div>
    )}
    
    <div className={`flex-1 max-w-2xl ${isUser ? 'flex justify-end' : ''}`}>
      <div className={`${isUser ? 'bg-synrgy-primary/10' : 'bg-synrgy-surface/30'} rounded-xl p-4 space-y-2`}>
        <Skeleton width="90%" height="1rem" />
        <Skeleton width="75%" height="1rem" />
        <Skeleton width="60%" height="1rem" />
        
        {/* Sometimes include a "visual" placeholder */}
        {Math.random() > 0.6 && (
          <div className="mt-4">
            <ChartSkeleton className="h-48" />
          </div>
        )}
      </div>
    </div>
  </motion.div>
)

// Loading Spinner with brand colors
export const LoadingSpinner: React.FC<{ 
  size?: 'sm' | 'md' | 'lg'
  className?: string 
}> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className={`${sizeClasses[size]} ${className}`}
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="2"
          className="opacity-20"
        />
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="url(#spinner-gradient)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray="31.416"
          strokeDashoffset="23.562"
        />
        <defs>
          <linearGradient id="spinner-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00EFFF" />
            <stop offset="100%" stopColor="#FF7A00" />
          </linearGradient>
        </defs>
      </svg>
    </motion.div>
  )
}

// Page Loading Screen
export const PageLoadingScreen: React.FC<{ message?: string }> = ({ 
  message = "Loading SYNRGY..." 
}) => (
  <div className="min-h-screen bg-synrgy-bg-950 flex items-center justify-center">
    <div className="text-center space-y-6">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-center gap-3"
      >
        <LoadingSpinner size="lg" className="text-synrgy-primary" />
        <span className="text-2xl font-heading font-bold text-gradient">ＳＹＮＲＧＹ</span>
      </motion.div>
      
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="text-synrgy-muted"
      >
        {message}
      </motion.p>
    </div>
  </div>
)
