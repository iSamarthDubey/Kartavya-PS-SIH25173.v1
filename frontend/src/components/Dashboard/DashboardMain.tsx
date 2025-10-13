import { useState } from 'react'
import { RefreshCw, Settings } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import VisualRenderer from '@/components/Visuals/VisualRenderer'
import DashboardGrid from './DashboardGrid'
import { windowsApi } from '@/services/api'
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

  // Fetch real Windows dashboard data
  const { data: dashboardData, refetch } = useQuery({
    queryKey: ['windows-dashboard-summary'],
    queryFn: windowsApi.getDashboardSummary,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 2,
    meta: {
      onError: (error: any) => {
        console.warn('Windows dashboard data fetch failed:', error)
      },
    },
  })

  // Fetch recent Windows events for activity section
  const { data: eventsData } = useQuery({
    queryKey: ['windows-recent-events'],
    queryFn: () => windowsApi.getRecentEvents(5),
    refetchInterval: 60000, // Refresh every minute
    retry: 1,
  })

  // Fetch system metrics for charts
  const { data: metricsData } = useQuery({
    queryKey: ['windows-system-metrics'],
    queryFn: () => windowsApi.getSystemMetrics('6h'),
    refetchInterval: 60000,
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

  // Use real data from APIs
  const summaryCards = dashboardData?.data?.summary_cards || []
  const recentEvents = eventsData?.data?.events || []
  const systemMetrics = metricsData?.data?.metrics || []
  const threatData = systemMetrics?.threat_timeline || []
  const topThreats = systemMetrics?.top_threats || []
  const geoData = systemMetrics?.geo_distribution || []
  const currentSystemHealth = dashboardData?.data?.system_health || systemHealth

  // If widgets are pinned and we're in hybrid mode, show the widget grid
  if (hybridMode && pinnedWidgets.length > 0) {
    return (
      <DashboardGrid
        hybridMode={hybridMode}
        onWidgetAction={onWidgetAction}
        className={className}
      />
    )
  }

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
        {/* Geographic Distribution */}
        <div>
          <VisualRenderer
            payload={createTablePayload(
              geoData.map((country: any) => ({
                Country: country.country || country.name,
                Threats: country.threats || 0,
                Status: country.threats > 50 ? 'High' : country.threats > 20 ? 'Medium' : 'Low',
              })),
              'Geographic Threat Distribution'
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

        {/* AI Insights */}
        <div>
          <VisualRenderer
            payload={createNarrativePayload(
              dashboardData?.data?.insights?.length > 0
                ? dashboardData.data.insights
                    .map((insight: any) => `• ${insight.message}`)
                    .join('\n\n')
                : 'ＳＹＮＲＧＹ is analyzing your security data and will provide insights shortly.',
              'ＳＹＮＲＧＹ Security Insights'
            )}
          />
        </div>
      </div>
    </div>
  )
}
