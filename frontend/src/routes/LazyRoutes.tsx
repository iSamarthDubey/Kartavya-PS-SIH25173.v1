/**
 * Lazy-loaded route components for optimal code splitting
 * These components are loaded on-demand to improve initial bundle size
 */

import { lazy } from 'react'

// Lazy load main page components
export const DashboardPage = lazy(() => import('@/pages/Dashboard'))
export const ChatPage = lazy(() => import('@/pages/Chat'))
export const HybridPage = lazy(() => import('@/pages/Hybrid'))
export const ReportsPage = lazy(() => import('@/pages/Reports'))
export const InvestigationsPage = lazy(() => import('@/pages/Investigations'))
export const AdminPage = lazy(() => import('@/pages/Admin'))
export const LoginPage = lazy(() => import('@/pages/Login'))

// Lazy load complex components
export const EnhancedVisualRenderer = lazy(() => import('@/components/Chat/EnhancedVisualRenderer'))

// Error boundary for lazy components
export { ErrorBoundary } from '@/components/ErrorBoundary'
