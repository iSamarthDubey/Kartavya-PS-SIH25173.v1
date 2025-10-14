import React, { Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'

// Import providers and core components
import { AuthProvider, useAuth } from '@/providers/AuthProvider'
import { WebSocketProvider } from '@/providers/WebSocketProvider'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import AppLayout from '@/components/Layout/AppLayout'
import LoadingScreen from '@/components/ui/LoadingScreen'

// Initialize performance monitoring
import { performanceMonitor } from '@/services/performance'

// Conditional DevTools for development
const DevTools = import.meta.env.DEV 
  ? React.lazy(() => import('@tanstack/react-query-devtools').then(module => ({ default: module.ReactQueryDevtools })))
  : React.lazy(() => Promise.resolve({ default: () => null }))

// Lazy load pages for better performance (as per SYNRGY.TXT)
const Landing = React.lazy(() => import('@/pages/Landing'))
const Login = React.lazy(() => import('@/pages/Login'))
const Dashboard = React.lazy(() => import('@/pages/Dashboard'))
const CommandCenter = React.lazy(() => import('@/pages/CommandCenter'))
const HybridConsole = React.lazy(() => import('@/pages/Hybrid'))
const Investigations = React.lazy(() => import('@/pages/Investigations'))
const Reports = React.lazy(() => import('@/pages/Reports'))
const Admin = React.lazy(() => import('@/pages/Admin'))


// Protected route wrapper with RBAC support
const ProtectedRoute: React.FC<{ 
  children: React.ReactNode
  requiredRole?: string
  requiredPermission?: string
}> = ({ children, requiredRole, requiredPermission }) => {
  const { isAuthenticated, isLoading, hasRole, hasPermission } = useAuth()
  
  // Show loading state while auth is being determined
  if (isLoading) {
    return <PageLoadingFallback />
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  // Check role-based access
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <div className="min-h-screen bg-synrgy-bg-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-synrgy-text mb-4">Access Denied</h1>
          <p className="text-synrgy-muted mb-6">You don't have permission to access this page.</p>
          <Navigate to="/app/dashboard" replace />
        </div>
      </div>
    )
  }
  
  // Check permission-based access
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-screen bg-synrgy-bg-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-synrgy-text mb-4">Access Denied</h1>
          <p className="text-synrgy-muted mb-6">You don't have the required permissions.</p>
          <Navigate to="/app/dashboard" replace />
        </div>
      </div>
    )
  }
  
  return <>{children}</>
}

// Loading fallback component
const PageLoadingFallback = () => (
  <div className="min-h-screen bg-synrgy-bg-900 flex items-center justify-center">
    <LoadingScreen message="Loading SYNRGY..." />
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <WebSocketProvider>
          <div className="min-h-screen bg-synrgy-bg-900 text-synrgy-text antialiased">
            <AnimatePresence mode="wait">
              <Suspense fallback={<PageLoadingFallback />}>
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<Landing />} />
                  <Route path="/login" element={<Login />} />
                  
                  {/* Protected routes with layout */}
                  <Route path="/app" element={
                    <ProtectedRoute>
                      <AppLayout />
                    </ProtectedRoute>
                  }>
                    <Route index element={<Navigate to="/app/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="chat" element={<CommandCenter />} />
                    <Route path="hybrid" element={<HybridConsole />} />
                    <Route path="reports" element={<Reports />} />
                    <Route path="investigations" element={<Investigations />} />
                    <Route path="admin" element={
                      <ProtectedRoute requiredRole="admin">
                        <Admin />
                      </ProtectedRoute>
                    } />
                  </Route>
                  
                  {/* Catch-all redirect */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </AnimatePresence>
          </div>
          
          {/* Dev tools only in development */}
          {import.meta.env.DEV && (
            <React.Suspense fallback={null}>
              <DevTools />
            </React.Suspense>
          )}
        </WebSocketProvider>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
