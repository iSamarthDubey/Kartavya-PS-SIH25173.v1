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

  // Fetch dashboard metrics - EVERY SECOND
  const { data: dashboardData, refetch } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.get('/dashboard/metrics'),
    refetchInterval: 1000, // Every 1 second
    refetchIntervalInBackground: true,
    retry: 2,
    staleTime: 0,
    meta: {
      onError: (error: any) => {
        console.warn('Dashboard metrics fetch failed:', error)
      },
    },
  })

  // Fetch alerts data - EVERY SECOND
  const { data: alertsData } = useQuery({
    queryKey: ['dashboard-alerts'],
    queryFn: () => api.get('/dashboard/alerts?limit=10'),
    refetchInterval: 1000, // Every 1 second
    refetchIntervalInBackground: true,
    staleTime: 0,
    retry: 1,
  })

  // Fetch system status - EVERY SECOND
  const { data: systemStatusData } = useQuery({
    queryKey: ['dashboard-system-status'],
    queryFn: () => api.get('/dashboard/system/status'),
    refetchInterval: 1000, // Every 1 second
    refetchIntervalInBackground: true,
    staleTime: 0,
    retry: 1,
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refetch()
    } finally {
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  // Extract ONLY backend API data - NO hardcoded values
  const backendMetrics = dashboardData?.data?.data || {}
  const alerts = alertsData?.data?.data || []
  const systemStatus = systemStatusData?.data?.data || []
  
  // Use ONLY backend data for summary cards
  const summaryCards = [
    {
      title: 'Total Threats',
      value: backendMetrics.totalThreats,
      change: { value: 0, trend: 'stable' as const, period: 'real-time' },
      status: backendMetrics.totalThreats > 50 ? 'critical' as const : backendMetrics.totalThreats > 20 ? 'warning' as const : 'normal' as const,
      color: 'primary'
    },
    {
      title: 'Active Alerts',
      value: backendMetrics.activeAlerts,
      change: { value: 0, trend: 'stable' as const, period: 'real-time' },
      status: backendMetrics.activeAlerts > 10 ? 'critical' as const : backendMetrics.activeAlerts > 5 ? 'warning' as const : 'normal' as const,
      color: 'accent'
    },
    {
      title: 'Systems Online',
      value: backendMetrics.systemsOnline,
      change: { value: 0, trend: 'stable' as const, period: 'real-time' },
      status: 'normal' as const,
      color: 'primary'
    },
    {
      title: 'Incidents Today',
      value: backendMetrics.incidentsToday,
      change: { value: 0, trend: 'stable' as const, period: 'today' },
      status: backendMetrics.incidentsToday > 10 ? 'warning' as const : 'normal' as const,
      color: 'primary'
    }
  ]
  
  // Use ONLY backend threatTrends data
  const threatData = backendMetrics.threatTrends?.map((trend: any) => ({
    x: trend.date,
    y: trend.count
  })) || []
  
  // Use ONLY backend topThreats data  
  const topThreats = backendMetrics.topThreats?.map((threat: any) => ({
    x: threat.name,
    y: threat.count
  })) || []
  
  // Use ONLY backend alerts data
  const recentEvents = alerts.slice(0, 5).map((alert: any) => ({
    timestamp: alert.timestamp || alert['@timestamp'],
    message: alert.message || alert.event?.action,
    host: alert.host?.name || alert.host,
    event_id: alert.id || alert.event?.code
  }))
  
  // Use ONLY backend system health data
  const currentSystemHealth = {
    health_score: backendMetrics.systemsOnline > 5 ? 'excellent' : backendMetrics.systemsOnline > 2 ? 'good' : 'degraded',
    services: {
      siem: backendMetrics.totalThreats !== undefined,
      pipeline: backendMetrics.activeAlerts !== undefined,
      connector: systemStatus.length > 0
    }
  }

  // Show pinned widgets grid if we're in hybrid mode AND have pinned widgets
  // Otherwise show the main dashboard with summary cards and charts

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-lg">Security Dashboard</h1>
          <p className="text-synrgy-muted">Real-time overview of your security posture</p>
        </div>

        <div className="flex items-center gap-3">
          {/* System Health */}
          <div className="flex items-center gap-2 text-sm">
            <div
              className={`w-2 h-2 rounded-full ${
                currentSystemHealth?.health_score === 'excellent'
                  ? 'bg-green-500'
                  : currentSystemHealth?.health_score === 'good'
                    ? 'bg-synrgy-accent'
                    : currentSystemHealth?.health_score === 'degraded'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
              }`}
            />
            <span className="text-synrgy-muted">
              System {currentSystemHealth?.health_score || 'Unknown'}
            </span>
          </div>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
            title="Refresh dashboard"
          >
            <RefreshCw
              className={`w-5 h-5 text-synrgy-muted ${refreshing ? 'animate-spin' : ''}`}
            />
          </button>

          {/* Settings */}
          <button className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors">
            <Settings className="w-5 h-5 text-synrgy-muted" />
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card: any, index: number) => (
          <div key={card.title} className="relative">
            <VisualRenderer
              payload={createSummaryCardPayload(card)}
            />
          </div>
        ))}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Timeline */}
        <div className="lg:col-span-2">
          <VisualRenderer
            payload={createChartPayload(threatData, 'Threat Activity Timeline', 'timeseries')}
          />
        </div>

        {/* Top Threats */}
        <div>
          <VisualRenderer
            payload={createChartPayload(topThreats, 'Top Threat Types', 'pie')}
          />
        </div>
      </div>

      {/* Secondary Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Status */}
        <div>
          <VisualRenderer
            payload={createTablePayload(
              systemStatus.map((system: any) => ({
                System: system.system || system.name || 'Unknown',
                Status: system.status || 'Unknown',
                CPU: system.cpu ? `${system.cpu}%` : 'N/A',
                Memory: system.memory ? `${system.memory}%` : 'N/A',
              })),
              'System Status'
            )}
          />
        </div>

        {/* Recent Activity */}
        <div>
          <VisualRenderer
            payload={createTablePayload(
              recentEvents.map((event: any) => ({
                Time: new Date(event.timestamp).toLocaleTimeString(),
                Message: event.message,
                Host: event.host,
                EventID: event.event_id,
              })),
              'Recent Security Events'
            )}
          />
        </div>

        {/* SYNRGY Real-Time Insights */}
        <div>
          <VisualRenderer
            payload={createNarrativePayload(
              backendMetrics.topThreats?.length > 0
                ? `**Real-time Threat Analysis:**\n\n${backendMetrics.topThreats.map((threat: any) => 
                    `• **${threat.name}**: ${threat.count} incidents (${threat.severity} severity)`
                  ).join('\n')}\n\n**System Status:** ${currentSystemHealth.health_score.toUpperCase()}\n\n**Active Monitoring:** ${backendMetrics.systemsOnline || 0} systems online`
                : `**ＳＹＮＲＧＹ Real-time Analysis**\n\nMonitoring ${backendMetrics.systemsOnline || 0} systems...\n\nActive threats: ${backendMetrics.totalThreats || 0}\nActive alerts: ${backendMetrics.activeAlerts || 0}`,
              'ＳＹＮＲＧＹ Real-Time Intelligence'
            )}
          />
        </div>
      </div>
    </div>
  )
}
