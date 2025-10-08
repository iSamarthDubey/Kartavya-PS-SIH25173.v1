/**
 * Loading States and Skeleton Components
 * Consistent loading UI patterns for the SIEM application
 */

import React from 'react';
import { Loader2, Shield, Activity, AlertTriangle, Users, BarChart3 } from 'lucide-react';

// ============= LOADING SPINNER =============

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'primary',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'text-blue-400',
    secondary: 'text-gray-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400'
  };

  return (
    <Loader2 
      className={`${sizeClasses[size]} ${colorClasses[color]} animate-spin ${className}`}
    />
  );
};

// ============= FULL PAGE LOADER =============

interface FullPageLoaderProps {
  message?: string;
  icon?: React.ReactNode;
}

export const FullPageLoader: React.FC<FullPageLoaderProps> = ({ 
  message = 'Loading SIEM Dashboard...', 
  icon 
}) => {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center">
      <div className="text-center space-y-6">
        {/* Icon or default SIEM shield */}
        <div className="w-16 h-16 mx-auto mb-6 bg-blue-600/20 rounded-full flex items-center justify-center">
          {icon || <Shield className="w-8 h-8 text-blue-400 animate-pulse" />}
        </div>

        {/* Loading spinner */}
        <LoadingSpinner size="lg" />
        
        {/* Loading message */}
        <div className="space-y-2">
          <p className="text-white text-lg font-medium">{message}</p>
          <div className="flex space-x-1 justify-center">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============= SKELETON COMPONENTS =============

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  className = '', 
  animate = true 
}) => {
  return (
    <div 
      className={`bg-gray-700/50 rounded ${animate ? 'animate-pulse' : ''} ${className}`}
    />
  );
};

// ============= CARD SKELETON =============

export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`bg-gray-800 border border-gray-700 rounded-lg p-6 ${className}`}>
      <div className="animate-pulse space-y-4">
        {/* Header */}
        <div className="flex items-center space-x-3">
          <Skeleton className="w-10 h-10 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
        
        {/* Content */}
        <div className="space-y-3">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
          <Skeleton className="h-3 w-3/4" />
        </div>
      </div>
    </div>
  );
};

// ============= DASHBOARD SKELETON =============

export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex justify-between items-center">
          <div className="space-y-2">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>

        {/* Stats Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="animate-pulse space-y-4">
                <div className="flex items-center justify-between">
                  <Skeleton className="w-8 h-8 rounded" />
                  <Skeleton className="w-16 h-6" />
                </div>
                <div className="space-y-2">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-4 w-24" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Grid Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="animate-pulse space-y-4">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-6 w-32" />
                  <Skeleton className="w-4 h-4 rounded-full" />
                </div>
                <Skeleton className="h-64 w-full rounded" />
              </div>
            </div>
          ))}
        </div>

        {/* Table Skeleton */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg">
          <div className="p-6 border-b border-gray-700">
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="divide-y divide-gray-700">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="p-4 animate-pulse">
                <div className="flex items-center space-x-4">
                  <Skeleton className="w-8 h-8 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-16" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============= CHAT SKELETON =============

export const ChatSkeleton: React.FC = () => {
  return (
    <div className="flex flex-col h-full">
      {/* Chat Header Skeleton */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center space-x-3 animate-pulse">
          <Skeleton className="w-10 h-10 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      </div>

      {/* Chat Messages Skeleton */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            {i % 2 === 0 ? (
              // User message
              <div className="flex justify-end">
                <div className="max-w-xs lg:max-w-md bg-blue-600/20 rounded-lg p-3 space-y-2">
                  <Skeleton className="h-3 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            ) : (
              // AI message
              <div className="flex items-start space-x-3">
                <Skeleton className="w-8 h-8 rounded-full" />
                <div className="max-w-xs lg:max-w-md bg-gray-700 rounded-lg p-3 space-y-2">
                  <Skeleton className="h-3 w-48" />
                  <Skeleton className="h-3 w-40" />
                  <Skeleton className="h-3 w-36" />
                </div>
              </div>
            )}
          </div>
        ))}
        
        {/* Typing indicator */}
        <div className="flex items-start space-x-3">
          <Skeleton className="w-8 h-8 rounded-full" />
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Chat Input Skeleton */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center space-x-3 animate-pulse">
          <Skeleton className="flex-1 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
        </div>
      </div>
    </div>
  );
};

// ============= TABLE SKELETON =============

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) => {
  return (
    <div className={`bg-gray-800 border border-gray-700 rounded-lg overflow-hidden ${className}`}>
      {/* Table Header */}
      <div className="p-4 border-b border-gray-700 animate-pulse">
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={i} className="h-4 w-full" />
          ))}
        </div>
      </div>

      {/* Table Body */}
      <div className="divide-y divide-gray-700">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4 animate-pulse">
            <div className="grid grid-cols-4 gap-4 items-center">
              {Array.from({ length: columns }).map((_, j) => (
                <Skeleton 
                  key={j} 
                  className={`h-4 ${j === 0 ? 'w-32' : j === columns - 1 ? 'w-16' : 'w-full'}`} 
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============= SPECIALIZED LOADING STATES =============

export const SecurityEventsSkeleton: React.FC = () => {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-start space-x-4 animate-pulse">
            <div className="flex-shrink-0">
              <AlertTriangle className="w-6 h-6 text-yellow-400 animate-pulse" />
            </div>
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-64" />
              <Skeleton className="h-3 w-48" />
              <div className="flex items-center space-x-4">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
            <Skeleton className="w-16 h-6 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
};

export const NetworkTrafficSkeleton: React.FC = () => {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="animate-pulse space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6 text-green-400" />
            <Skeleton className="h-5 w-32" />
          </div>
          <Skeleton className="w-20 h-6 rounded-full" />
        </div>
        
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Skeleton className="w-8 h-8 rounded-full" />
                <div className="space-y-1">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-2 w-16" />
                </div>
              </div>
              <Skeleton className="h-3 w-16" />
            </div>
          ))}
        </div>
        
        <Skeleton className="h-32 w-full rounded" />
      </div>
    </div>
  );
};

export const UserActivitySkeleton: React.FC = () => {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="animate-pulse space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Users className="w-6 h-6 text-blue-400" />
            <Skeleton className="h-5 w-32" />
          </div>
          <Skeleton className="w-24 h-8 rounded" />
        </div>
        
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <Skeleton className="w-10 h-10 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-16" />
                </div>
                <Skeleton className="h-3 w-48" />
              </div>
              <Skeleton className="w-12 h-6 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============= INLINE LOADING =============

interface InlineLoadingProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const InlineLoading: React.FC<InlineLoadingProps> = ({ 
  text = 'Loading...', 
  size = 'md',
  className = ''
}) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <LoadingSpinner size={size} />
      <span className="text-gray-300">{text}</span>
    </div>
  );
};

// ============= BUTTON LOADING STATE =============

interface LoadingButtonProps {
  loading?: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  children,
  className = '',
  onClick,
  disabled = false
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        flex items-center justify-center space-x-2 px-4 py-2 rounded-lg
        transition-colors duration-200
        ${disabled || loading 
          ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
          : 'bg-blue-600 hover:bg-blue-700 text-white'
        }
        ${className}
      `}
    >
      {loading && <LoadingSpinner size="sm" />}
      <span>{children}</span>
    </button>
  );
};

// ============= PROGRESS BAR =============

interface ProgressBarProps {
  progress: number; // 0-100
  className?: string;
  color?: 'primary' | 'success' | 'warning' | 'error';
  showPercentage?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className = '',
  color = 'primary',
  showPercentage = false
}) => {
  const colorClasses = {
    primary: 'bg-blue-400',
    success: 'bg-green-400',
    warning: 'bg-yellow-400',
    error: 'bg-red-400'
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
      {showPercentage && (
        <div className="text-right">
          <span className="text-sm text-gray-400">{Math.round(progress)}%</span>
        </div>
      )}
    </div>
  );
};

// ============= EXPORTS =============

export default {
  LoadingSpinner,
  FullPageLoader,
  Skeleton,
  CardSkeleton,
  DashboardSkeleton,
  ChatSkeleton,
  TableSkeleton,
  SecurityEventsSkeleton,
  NetworkTrafficSkeleton,
  UserActivitySkeleton,
  InlineLoading,
  LoadingButton,
  ProgressBar
};
