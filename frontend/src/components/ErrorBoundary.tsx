/**
 * Error Boundary Components
 * Comprehensive error handling for the SIEM application
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

// ============= MAIN ERROR BOUNDARY =============

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to monitoring service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send error to backend for logging
    this.logErrorToBackend(error, errorInfo);
  }

  private logErrorToBackend = async (error: Error, errorInfo: ErrorInfo) => {
    try {
      // Only log in production or when backend is available
      if (import.meta.env.PROD) {
        const errorData = {
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        };

        // Send to monitoring endpoint
        await fetch('/api/errors', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(errorData),
        });
      }
    } catch (logError) {
      console.error('Failed to log error to backend:', logError);
    }
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  private handleReset = () => {
    // Clear local storage and reload
    localStorage.clear();
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onRetry={this.handleRetry}
          onReset={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}

// ============= ERROR FALLBACK UI =============

interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  onRetry: () => void;
  onReset: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  onRetry,
  onReset,
}) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-gray-800 border border-red-700/50 rounded-xl p-8 text-center">
          {/* Error Icon */}
          <div className="w-16 h-16 mx-auto mb-6 bg-red-600/20 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>

          {/* Error Message */}
          <h1 className="text-2xl font-bold text-white mb-4">
            Oops! Something went wrong
          </h1>
          
          <p className="text-gray-300 mb-6">
            The SIEM application encountered an unexpected error. 
            This has been automatically reported to our team.
          </p>

          {error && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-6 text-left">
              <p className="text-red-400 font-mono text-sm">
                {error.message}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <button
              onClick={onRetry}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Try Again</span>
            </button>

            <button
              onClick={onReset}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              <Home className="w-4 h-4" />
              <span>Reset App</span>
            </button>
          </div>

          {/* Debug Details */}
          <div className="border-t border-gray-700 pt-6">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center justify-center space-x-2 text-gray-400 hover:text-white transition-colors mx-auto"
            >
              <Bug className="w-4 h-4" />
              <span>{showDetails ? 'Hide' : 'Show'} Technical Details</span>
            </button>

            {showDetails && (
              <div className="mt-4 bg-gray-900 border border-gray-700 rounded-lg p-4 text-left">
                <h3 className="text-white font-semibold mb-2">Error Stack:</h3>
                <pre className="text-xs text-gray-400 whitespace-pre-wrap overflow-x-auto">
                  {error?.stack}
                </pre>
                
                {errorInfo && (
                  <>
                    <h3 className="text-white font-semibold mb-2 mt-4">Component Stack:</h3>
                    <pre className="text-xs text-gray-400 whitespace-pre-wrap overflow-x-auto">
                      {errorInfo.componentStack}
                    </pre>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Support Info */}
          <div className="mt-6 text-xs text-gray-500">
            <p>Error ID: {Date.now()}</p>
            <p>Time: {new Date().toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============= SPECIALIZED ERROR BOUNDARIES =============

// API Error Boundary
export const ApiErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-6 bg-red-900/20 border border-red-700/50 rounded-lg">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h3 className="text-white font-semibold">API Connection Error</h3>
          </div>
          <p className="text-gray-300 mb-4">
            Unable to connect to the SIEM backend. Please check your connection.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Retry Connection
          </button>
        </div>
      }
      onError={(error, errorInfo) => {
        console.error('API Error:', error, errorInfo);
      }}
    >
      {children}
    </ErrorBoundary>
  );
};

// Dashboard Error Boundary
export const DashboardErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-6 bg-yellow-900/20 border border-yellow-700/50 rounded-lg">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <h3 className="text-white font-semibold">Dashboard Error</h3>
          </div>
          <p className="text-gray-300">
            The dashboard encountered an error loading security metrics.
          </p>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};

// Chat Error Boundary
export const ChatErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-6 bg-blue-900/20 border border-blue-700/50 rounded-lg">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-blue-400" />
            <h3 className="text-white font-semibold">Chat Interface Error</h3>
          </div>
          <p className="text-gray-300">
            The SIEM assistant is temporarily unavailable.
          </p>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};

// ============= ERROR HOOK =============

export const useErrorHandler = () => {
  const handleError = React.useCallback((error: Error, context?: string) => {
    console.error(`Error${context ? ` in ${context}` : ''}:`, error);
    
    // Could dispatch to global error state here
    // For now, just log to console
  }, []);

  return handleError;
};

// ============= EXPORTS =============

export default ErrorBoundary;
