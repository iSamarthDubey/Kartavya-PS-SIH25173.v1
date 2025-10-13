/**
 * Enhanced ErrorBoundary with backend error reporting
 * Reports client-side errors to backend for monitoring and debugging
 */

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  errorId: string | null
  reporting: boolean
}

// Error reporting service with throttling
class ErrorReportingService {
  private static instance: ErrorReportingService
  private reportedErrors = new Set<string>()
  private reportQueue: Array<any> = []
  private isReporting = false
  private maxReportsPerSession = 50
  private reportsSent = 0

  static getInstance(): ErrorReportingService {
    if (!ErrorReportingService.instance) {
      ErrorReportingService.instance = new ErrorReportingService()
    }
    return ErrorReportingService.instance
  }

  private getErrorSignature(error: Error): string {
    // Create a unique signature for the error to prevent duplicate reporting
    return `${error.name}:${error.message}:${error.stack?.split('\n')[1] || 'unknown'}`
  }

  private async reportToBackend(errorData: any): Promise<void> {
    try {
      // Only report if error reporting is enabled and we haven't exceeded limits
      if (
        import.meta.env.VITE_ENABLE_ERROR_REPORTING !== 'true' ||
        this.reportsSent >= this.maxReportsPerSession
      ) {
        return
      }

      const response = await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      })

      if (response.ok) {
        this.reportsSent++
        if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
          console.log('Error reported to backend:', errorData.errorId)
        }
      }
    } catch (reportError) {
      // Silently fail error reporting to avoid infinite loops
      if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
        console.warn('Failed to report error to backend:', reportError)
      }
    }
  }

  async reportError(error: Error, errorInfo: ErrorInfo, context: any = {}): Promise<string> {
    const errorSignature = this.getErrorSignature(error)

    // Skip if already reported
    if (this.reportedErrors.has(errorSignature)) {
      return ''
    }

    // Mark as reported
    this.reportedErrors.add(errorSignature)

    // Generate unique error ID
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    const errorData = {
      errorId,
      timestamp: new Date().toISOString(),
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
        signature: errorSignature,
      },
      errorInfo: {
        componentStack: errorInfo.componentStack,
      },
      context: {
        ...context,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
      },
      session: {
        sessionId: sessionStorage.getItem('synrgy_session_id') || 'anonymous',
        userId: localStorage.getItem('synrgy_user_id') || 'anonymous',
      },
      severity: this.calculateSeverity(error),
    }

    // Add to report queue
    this.reportQueue.push(errorData)

    // Process queue
    if (!this.isReporting) {
      this.processReportQueue()
    }

    return errorId
  }

  private calculateSeverity(error: Error): 'low' | 'medium' | 'high' | 'critical' {
    // Determine error severity based on error type and message
    if (error.name === 'ChunkLoadError' || error.message.includes('Loading chunk')) {
      return 'medium' // Code splitting issues
    }

    if (error.message.includes('Network Error') || error.message.includes('fetch')) {
      return 'medium' // Network issues
    }

    if (error.stack?.includes('React') || error.stack?.includes('useState')) {
      return 'high' // React errors
    }

    return 'high' // Default to high for uncaught errors
  }

  private async processReportQueue(): Promise<void> {
    if (this.isReporting || this.reportQueue.length === 0) {
      return
    }

    this.isReporting = true

    while (this.reportQueue.length > 0 && this.reportsSent < this.maxReportsPerSession) {
      const errorData = this.reportQueue.shift()
      if (errorData) {
        await this.reportToBackend(errorData)
        // Small delay between reports
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }

    this.isReporting = false
  }
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private errorReporter = ErrorReportingService.getInstance()

  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      reporting: false,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    }
  }

  async componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ reporting: true })

    try {
      // Report error to backend
      const errorId = await this.errorReporter.reportError(error, errorInfo, {
        component: 'ErrorBoundary',
        props: this.props,
      })

      this.setState({
        errorInfo,
        errorId,
        reporting: false,
      })

      // Call custom error handler if provided
      this.props.onError?.(error, errorInfo)
    } catch (reportError) {
      this.setState({ reporting: false })
      console.error('Failed to report error:', reportError)
    }
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      reporting: false,
    })
  }

  private handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 dark:bg-red-900 rounded-full mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>

            <div className="text-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Something went wrong
              </h1>

              <p className="text-gray-600 dark:text-gray-300 mb-4">
                An unexpected error occurred. The error has been automatically reported.
              </p>

              {this.state.errorId && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-4 font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded">
                  Error ID: {this.state.errorId}
                </p>
              )}

              {import.meta.env.VITE_ENABLE_DEBUG === 'true' && this.state.error && (
                <details className="text-left mb-4 text-sm">
                  <summary className="cursor-pointer text-gray-600 dark:text-gray-300 font-medium">
                    Technical Details
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-xs overflow-auto">
                    {this.state.error.name}: {this.state.error.message}
                    {this.state.error.stack && (
                      <>
                        {'\n\n'}
                        {this.state.error.stack}
                      </>
                    )}
                  </pre>
                </details>
              )}

              <div className="flex space-x-3">
                <button
                  onClick={this.handleRetry}
                  disabled={this.state.reporting}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {this.state.reporting ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Reporting...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Try Again
                    </>
                  )}
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// React hook for manual error reporting
export const useErrorReporting = () => {
  const errorReporter = ErrorReportingService.getInstance()

  const reportError = React.useCallback(
    (error: Error, context: any = {}) => {
      return errorReporter.reportError(error, { componentStack: '' } as ErrorInfo, context)
    },
    [errorReporter]
  )

  return { reportError }
}

export default ErrorBoundary
