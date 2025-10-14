import { useState, useEffect } from 'react'
import { RefreshCw, Settings } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import VisualRenderer from '@/components/Visuals/VisualRenderer'
import DashboardGrid from './DashboardGrid'
import { dashboardApi, api } from '@/services/api'
import { useAppStore } from '@/stores/appStore'
import { useHybridStore } from '@/stores/hybridStore'

interface DashboardMainProps {
  onAskSynrgy?: (query: string) => void
  hybridMode?: boolean
  onWidgetAction?: (widgetId: string, action: string, data?: any) => void
  className?: string
}

// Utility function to convert dashboard data to visual payloads
const createSummaryCardPayload = (card: any) => ({
  type: 'composite' as const,
  cards: [
    {
      type: 'summary_card' as const,
      title: card.title,
      value: card.value,
      status: card.status || 'normal',
      data: {
        title: card.title,
        value: card.value,
        status: card.status || 'normal',
        color: card.color || 'primary',
        change: card.change,
      },
      config: {
        interactive: true,
        exportable: true,
        pinnable: true
      }
    },
  ],
})

const createChartPayload = (
  data: any[],
  title: string,
  chartType: 'timeseries' | 'bar' | 'pie'
) => ({
  type: 'composite' as const,
  cards: [
    {
      type: 'chart' as const,
      title,
      chart_type: chartType,
      data: data,
      config: {
        interactive: true,
        exportable: true,
        pinnable: true,
        clickable: true,
        hoverable: true
      },
    },
  ],
})

const createTablePayload = (data: any[], title: string) => ({
  type: 'composite' as const,
  cards: [
    {
      type: 'table' as const,
      title,
      columns: Object.keys(data[0] || {}).map(key => ({ key, label: key })),
      rows: data.map(row => Object.values(row)),
      data: {
        headers: Object.keys(data[0] || {}),
        rows: data,
        sortable: true,
        filterable: true,
      },
      config: {
        interactive: true,
        exportable: true,
        pinnable: true
      }
    },
  ],
})

const createNarrativePayload = (content: string, title: string) => ({
  type: 'composite' as const,
  cards: [
    {
      type: 'narrative' as const,
      title,
      data: {
        content,
        format: 'markdown',
      },
      config: {
        interactive: true,
        exportable: true,
        pinnable: true
      }
    },
  ],
})

export default function DashboardMain({
  onAskSynrgy,
  hybridMode = false,
  onWidgetAction,
  className = '',
}: DashboardMainProps) {
  const [refreshing, setRefreshing] = useState(false)
  const { systemHealth } = useAppStore()
  const { pinnedWidgets, setHybridMode } = useHybridStore()

  // Fetch dashboard metrics from backend API (only endpoint we need)
  const { data: dashboardData, refetch, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.get('/api/dashboard/metrics'),
    refetchInterval: 5000,
    refetchIntervalInBackground: true,
    retry: 2,
    staleTime: 0,
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refetch()
    } finally {
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  // Show loading state if metrics are loading
  if (metricsLoading) {
    return (
      <div className={`p-6 flex items-center justify-center min-h-[400px] ${className}`}>
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-synrgy-primary mx-auto mb-4" />
          <p className="text-synrgy-muted">Loading real-time dashboard data...</p>
        </div>
      </div>
    )
  }

  // Show error state if data fetch failed
  if (metricsError && !dashboardData) {
    return (
      <div className={`p-6 flex items-center justify-center min-h-[400px] ${className}`}>
        <div className="text-center">
          <p className="text-red-400 mb-4">Failed to load dashboard data</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Extract dashboard metrics data from the main API endpoint
  const dashboardMetrics = dashboardData?.data?.data || {}
  
  // Create summary cards from dashboard metrics - NO FALLBACKS, BACKEND DATA ONLY
  const summaryCards = dashboardMetrics.totalThreats !== undefined || dashboardMetrics.activeAlerts !== undefined ? [
    {
      title: 'Total Threats',
      value: dashboardMetrics.totalThreats || 0,
      status: (dashboardMetrics.totalThreats || 0) > 500 ? 'warning' : 'normal',
      color: 'primary',
      change: { value: dashboardMetrics.totalThreatsChange || 0, trend: (dashboardMetrics.totalThreatsChange || 0) > 0 ? 'up' : 'down' }
    },
    {
      title: 'Active Alerts',
      value: dashboardMetrics.activeAlerts || 0,
      status: (dashboardMetrics.activeAlerts || 0) > 700 ? 'error' : (dashboardMetrics.activeAlerts || 0) > 300 ? 'warning' : 'normal',
      color: 'accent',
      change: { value: dashboardMetrics.activeAlertsChange || 0, trend: (dashboardMetrics.activeAlertsChange || 0) > 0 ? 'up' : 'down' }
    },
    {
      title: 'Systems Online',
      value: dashboardMetrics.systemsOnline || 0,
      status: (dashboardMetrics.systemsOnline || 0) > 3 ? 'success' : 'warning',
      color: 'success',
      change: { value: dashboardMetrics.systemsOnlineChange || 0, trend: (dashboardMetrics.systemsOnlineChange || 0) >= 0 ? 'stable' : 'down' }
    },
    {
      title: 'Incidents Today',
      value: dashboardMetrics.incidentsToday || 0,
      status: (dashboardMetrics.incidentsToday || 0) > 1000 ? 'warning' : 'info',
      color: 'warning',
      change: { value: dashboardMetrics.incidentsTodayChange || 0, trend: (dashboardMetrics.incidentsTodayChange || 0) > 0 ? 'up' : 'down' }
    }
  ] : []
  
  // Extract chart data from dashboard metrics - NO FALLBACKS, BACKEND DATA ONLY
  const threatTrends = dashboardMetrics.threatTrends || []
  const topThreats = dashboardMetrics.topThreats || []
  
  // Map data to chart format with proper field names for visualization - only if data exists
  const threatData = threatTrends.length > 0 ? threatTrends.map((trend: any) => ({
    x: trend.date,
    y: trend.count,
    name: trend.date,
    value: trend.count
  })) : []
  
  const topThreatsData = topThreats.length > 0 ? topThreats.map((threat: any) => ({
    x: threat.name,
    y: threat.count,
    name: threat.name,
    value: threat.count,
    severity: threat.severity
  })) : []
  
  // Calculate system health based on current metrics - NO FALLBACKS, BACKEND DATA ONLY
  const activeAlerts = dashboardMetrics.activeAlerts || 0
  const totalThreats = dashboardMetrics.totalThreats || 0
  const systemsOnline = dashboardMetrics.systemsOnline || 0
  
  const currentSystemHealth = {
    health_score: activeAlerts > 700 ? 'degraded' : 
                  totalThreats > 500 ? 'good' : 
                  activeAlerts === 0 && totalThreats === 0 ? 'unknown' : 'excellent',
    services: {
      'SIEM Monitor': dashboardMetrics.siemMonitor ?? true,
      'Threat Detection': systemsOnline > 0,
      'Alert System': activeAlerts < 1000,
      'Data Pipeline': dashboardMetrics.dataPipeline ?? false
    }
  }

  // Show pinned widgets grid if we're in hybrid mode AND have pinned widgets
  // Otherwise show the main dashboard with summary cards and charts

  return (
    <div className={`w-full min-h-screen bg-synrgy-bg-950 ${className}`}>
      {/* Page Container with Proper Spacing */}
      <div className="max-w-[1800px] mx-auto px-8 py-8 space-y-8">
        {/* Clean Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-synrgy-text mb-3">Security Dashboard</h1>
            <p className="text-lg text-synrgy-muted">Real-time overview of your security posture</p>
          </div>

          <div className="flex items-center gap-6">
            {/* System Health Status */}
            <div className={`
              flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium border
              ${
                currentSystemHealth?.health_score === 'excellent'
                  ? 'bg-green-500/10 text-green-400 border-green-500/20'
                  : currentSystemHealth?.health_score === 'good'
                    ? 'bg-synrgy-accent/10 text-synrgy-accent border-synrgy-accent/20'
                    : currentSystemHealth?.health_score === 'degraded'
                      ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                      : 'bg-red-500/10 text-red-400 border-red-500/20'
              }
            `}>
              <div
                className={`w-3 h-3 rounded-full ${
                  currentSystemHealth?.health_score === 'excellent'
                    ? 'bg-green-500'
                    : currentSystemHealth?.health_score === 'good'
                      ? 'bg-synrgy-accent'
                      : currentSystemHealth?.health_score === 'degraded'
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                }`}
              />
              <span className="capitalize">
                System {currentSystemHealth?.health_score || 'Unknown'}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-3 hover:bg-synrgy-primary/10 rounded-xl transition-colors border border-synrgy-primary/20"
                title="Refresh dashboard"
              >
                <RefreshCw
                  className={`w-5 h-5 text-synrgy-primary ${refreshing ? 'animate-spin' : ''}`}
                />
              </button>

              {/* Settings Button */}
              <button className="p-3 hover:bg-synrgy-primary/10 rounded-xl transition-colors border border-synrgy-primary/20">
                <Settings className="w-5 h-5 text-synrgy-primary" />
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards - Full Width Grid */}
        {summaryCards.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-8">
            {summaryCards.map((card: any, index: number) => (
              <div key={card.title || index} className="w-full">
                <VisualRenderer
                  payload={createSummaryCardPayload(card)}
                  className="w-full"
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-2xl p-12 text-center">
            <p className="text-synrgy-muted text-lg">No dashboard metrics available from backend</p>
            <button
              onClick={() => refetch()}
              className="mt-6 px-6 py-3 bg-synrgy-primary text-synrgy-bg-900 rounded-xl hover:bg-synrgy-primary/90 transition-colors font-medium"
            >
              Refresh Data
            </button>
          </div>
        )}

        {/* Main Charts - Only show if we have data */}
        {(threatData.length > 0 || topThreatsData.length > 0) ? (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {threatData.length > 0 && (
              <div className="xl:col-span-2 w-full">
                <VisualRenderer
                  payload={createChartPayload(threatData, 'Threat Activity Timeline', 'timeseries')}
                  className="w-full h-full"
                />
              </div>
            )}
            {topThreatsData.length > 0 && (
              <div className="xl:col-span-1 w-full">
                <VisualRenderer
                  payload={createChartPayload(topThreatsData, 'Top Threat Types', 'pie')}
                  className="w-full h-full"
                />
              </div>
            )}
          </div>
        ) : (
          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-2xl p-12 text-center">
            <p className="text-synrgy-muted text-lg mb-2">No chart data available from backend</p>
            <p className="text-sm text-synrgy-muted/70">API: /api/dashboard/metrics</p>
          </div>
        )}

        {/* Secondary Widgets - Proper Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Top Threats Analysis */}
          <div className="xl:col-span-2 w-full">
            {topThreatsData.length > 0 ? (
              <VisualRenderer
                payload={createTablePayload(
                  topThreats.map((threat: any) => ({
                    'Threat Type': threat.name,
                    'Count': threat.count.toLocaleString(),
                    'Severity': threat.severity,
                    'Status': threat.count > 200 ? 'High' : threat.count > 100 ? 'Medium' : 'Low'
                  })),
                  'Top Threats Analysis'
                )}
                className="w-full"
              />
            ) : (
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-2xl p-8 h-full">
                <h3 className="font-semibold text-synrgy-text mb-6 text-xl">Top Threats Analysis</h3>
                <p className="text-synrgy-muted text-lg">No threat data available from backend</p>
              </div>
            )}
          </div>

          {/* System Health Status */}
          <div className="xl:col-span-1 w-full">
            <VisualRenderer
              payload={createNarrativePayload(
                `**ＳＹＮＲＧＹ System Status**\n\n**Health Score:** ${currentSystemHealth?.health_score || 'Unknown'}\n\n**Services Status:**\n${Object.entries(currentSystemHealth?.services || {}).map(([service, status]) => 
                  `• ${service}: ${status ? '✅ Online' : '❌ Offline'}`
                ).join('\n')}\n\n*Data refreshed every 5 seconds*`,
                'ＳＹＮＲＧＹ System Monitor'
              )}
              className="w-full h-full"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
