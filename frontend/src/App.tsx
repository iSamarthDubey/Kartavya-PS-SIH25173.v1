import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAppStore, useAuth } from '@/stores/appStore'

// Page components
import LandingPage from '@/pages/Landing'
import LoginPage from '@/pages/Login'
import DashboardPage from '@/pages/Dashboard'
import ChatPage from '@/pages/Chat'
import HybridPage from '@/pages/Hybrid'
import ReportsPage from '@/pages/Reports'
import InvestigationsPage from '@/pages/Investigations'
import AdminPage from '@/pages/Admin'
import SettingsPage from '@/pages/Settings'

// Layout components
import AppLayout from '@/components/Layout/AppLayout'
import LoadingScreen from '@/components/ui/LoadingScreen'

// Utility to check if route requires authentication
const protectedRoutes = ['/dashboard', '/chat', '/hybrid', '/reports', '/investigations', '/admin', '/settings']

function App() {
  const { isAuthenticated, user } = useAuth()
  const { loading, setMode, checkSystemHealth } = useAppStore()
  const location = useLocation()

  // Initialize app on mount
  useEffect(() => {
    // Check system health on app load
    checkSystemHealth()
    
    // Set initial mode based on route
    const path = location.pathname
    if (path === '/') {
      setMode('landing')
    } else if (path === '/login') {
      setMode('landing')
    } else if (path === '/dashboard') {
      setMode('dashboard')
    } else if (path === '/chat') {
      setMode('chat')
    } else if (path === '/hybrid') {
      setMode('hybrid')
    } else if (path === '/reports') {
      setMode('reports')
    } else if (path === '/investigations') {
      setMode('investigations')
    } else if (path === '/admin') {
      setMode('admin')
    } else if (path === '/settings') {
      setMode('settings')
    }
  }, [checkSystemHealth, setMode, location.pathname])

  // Route protection logic
  const isProtectedRoute = protectedRoutes.some(route => location.pathname.startsWith(route))
  const shouldRedirectToLogin = isProtectedRoute && !isAuthenticated

  // Show loading screen during initial app load
  if (loading) {
    return <LoadingScreen message="Initializing ＳＹＮＲＧＹ..." />
  }

  return (
    <div className="min-h-screen bg-synrgy-bg-900 text-synrgy-text">
      <Routes>
        {/* Public routes */}
        <Route 
          path="/" 
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LandingPage />
            )
          } 
        />
        
        <Route 
          path="/login" 
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage />
            )
          } 
        />

        {/* Protected routes */}
        <Route 
          path="/dashboard" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/chat" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <ChatPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/hybrid" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <HybridPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/reports" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <ReportsPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/investigations" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <InvestigationsPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/admin" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : user?.role !== 'admin' ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AppLayout>
                <AdminPage />
              </AppLayout>
            )
          } 
        />
        
        <Route 
          path="/settings" 
          element={
            shouldRedirectToLogin ? (
              <Navigate to="/login" replace />
            ) : (
              <AppLayout>
                <SettingsPage />
              </AppLayout>
            )
          } 
        />

        {/* 404 fallback */}
        <Route 
          path="*" 
          element={
            <div className="min-h-screen bg-synrgy-bg-900 text-synrgy-text flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-8 bg-synrgy-primary/10 rounded-full flex items-center justify-center">
                  <svg className="w-12 h-12 text-synrgy-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.034 0-3.9.785-5.291 2.068M6.343 7.343A8 8 0 0012 4c4.418 0 8 3.582 8 8 0 1.867-.643 3.582-1.721 4.657" />
                  </svg>
                </div>
                
                <h1 className="heading-lg mb-4">
                  Page Not Found
                </h1>
                
                <p className="text-synrgy-muted mb-8 max-w-md mx-auto">
                  The page you're looking for doesn't exist or has been moved.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => window.history.back()}
                    className="btn-secondary"
                  >
                    Go Back
                  </button>
                  
                  <button
                    onClick={() => window.location.href = isAuthenticated ? '/dashboard' : '/'}
                    className="btn-primary"
                  >
                    {isAuthenticated ? 'Go to Dashboard' : 'Go to Home'}
                  </button>
                </div>
              </div>
            </div>
          } 
        />
      </Routes>
    </div>
  )
}

export default App
