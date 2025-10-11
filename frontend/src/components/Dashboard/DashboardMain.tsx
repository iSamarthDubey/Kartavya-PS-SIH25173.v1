import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Activity, 
  MessageSquare,
  RefreshCw,
  Settings,
  TrendingUp,
  Globe,
  Zap
} from 'lucide-react'
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import { useQuery } from '@tanstack/react-query'

import SummaryCardComponent from './SummaryCard'
import DashboardGrid from './DashboardGrid'
import { dashboardApi, windowsApi } from '@/services/api'
import { useAppStore } from '@/stores/appStore'
import { useHybridStore } from '@/stores/hybridStore'
import type { SummaryCard } from '@/types'

interface DashboardMainProps {
  onAskSynrgy?: (query: string) => void
  hybridMode?: boolean
  onWidgetAction?: (widgetId: string, action: string, data?: any) => void
  className?: string
}

// Dynamic data colors for charts
const CHART_COLORS = ['#FF7A00', '#00EFFF', '#22D3EE', '#F97316', '#06B6D4', '#EA580C']

export default function DashboardMain({ 
  onAskSynrgy, 
  hybridMode = false, 
  onWidgetAction,
  className = '' 
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
      }
    }
  })

  // Fetch recent Windows events for activity section
  const { data: eventsData } = useQuery({
    queryKey: ['windows-recent-events'],
    queryFn: () => windowsApi.getRecentEvents(5),
    refetchInterval: 60000, // Refresh every minute
    retry: 1
  })

  // Fetch system metrics for charts
  const { data: metricsData } = useQuery({
    queryKey: ['windows-system-metrics'],
    queryFn: () => windowsApi.getSystemMetrics('6h'),
    refetchInterval: 60000,
    retry: 1
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
          <p className="text-synrgy-muted">
            Real-time overview of your security posture
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* System Health */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              currentSystemHealth?.health_score === 'excellent' ? 'bg-green-500' :
              currentSystemHealth?.health_score === 'good' ? 'bg-synrgy-accent' :
              currentSystemHealth?.health_score === 'degraded' ? 'bg-yellow-500' :
              'bg-red-500'
            }`} />
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
            <RefreshCw className={`w-5 h-5 text-synrgy-muted ${refreshing ? 'animate-spin' : ''}`} />
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
          <SummaryCardComponent
            key={card.title}
            card={card}
            index={index}
            onAskSynrgy={onAskSynrgy}
          />
        ))}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Timeline */}
        <div className="lg:col-span-2 bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-synrgy-primary" />
              </div>
              <h3 className="text-lg font-semibold text-synrgy-text">Threat Activity</h3>
            </div>
            
            {onAskSynrgy && (
              <button
                onClick={() => onAskSynrgy("Tell me about the threat activity trends and any patterns you notice")}
                className="flex items-center gap-2 text-sm text-synrgy-primary hover:bg-synrgy-primary/10 px-3 py-1.5 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4" />
                Ask SYNRGY
              </button>
            )}
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={threatData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
                <XAxis 
                  dataKey="name" 
                  stroke="#94A3B8" 
                  fontSize={12}
                  tick={{ fill: '#94A3B8' }}
                />
                <YAxis 
                  stroke="#94A3B8" 
                  fontSize={12}
                  tick={{ fill: '#94A3B8' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F1724',
                    border: '1px solid #00EFFF',
                    borderRadius: '8px',
                    color: '#E6EEF8'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="threats" 
                  stroke="#FF7A00" 
                  strokeWidth={2}
                  fill="url(#threatGradient)"
                />
                <Area 
                  type="monotone" 
                  dataKey="blocked" 
                  stroke="#00EFFF" 
                  strokeWidth={2}
                  fill="url(#blockedGradient)"
                />
                <defs>
                  <linearGradient id="threatGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF7A00" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#FF7A00" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="blockedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00EFFF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00EFFF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Threats */}
        <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-synrgy-accent/10 rounded-lg flex items-center justify-center">
                <Shield className="w-4 h-4 text-synrgy-accent" />
              </div>
              <h3 className="text-lg font-semibold text-synrgy-text">Top Threats</h3>
            </div>
            
            {onAskSynrgy && (
              <button
                onClick={() => onAskSynrgy("Show me details about the top threat types and their impact")}
                className="p-1.5 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4 text-synrgy-primary" />
              </button>
            )}
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={topThreats}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {topThreats.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color || CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F1724',
                    border: '1px solid #00EFFF',
                    borderRadius: '8px',
                    color: '#E6EEF8'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="space-y-2">
            {topThreats.length > 0 ? topThreats.map((threat: any, index: number) => (
              <div key={threat.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: threat.color || CHART_COLORS[index % CHART_COLORS.length] }} />
                  <span className="text-synrgy-text">{threat.name}</span>
                </div>
                <span className="text-synrgy-muted">{threat.value}%</span>
              </div>
            )) : (
              <div className="text-center text-synrgy-muted py-4">
                <p className="text-sm">No threat data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Secondary Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Geographic Distribution */}
        <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                <Globe className="w-4 h-4 text-synrgy-primary" />
              </div>
              <h3 className="text-lg font-semibold text-synrgy-text">Geo Distribution</h3>
            </div>
            
            {onAskSynrgy && (
              <button
                onClick={() => onAskSynrgy("Show me geographic threat distribution and any regional patterns")}
                className="p-1.5 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4 text-synrgy-primary" />
              </button>
            )}
          </div>

          <div className="space-y-3">
            {geoData.length > 0 ? geoData.map((country: any, index: number) => {
              const maxThreats = Math.max(...geoData.map((c: any) => c.threats || 0))
              return (
                <motion.div
                  key={country.country || country.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-synrgy-accent rounded-full" />
                    <span className="text-sm text-synrgy-text">{country.country || country.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-synrgy-surface rounded-full h-2">
                      <div 
                        className="h-2 bg-synrgy-accent rounded-full transition-all duration-500"
                        style={{ width: `${maxThreats > 0 ? ((country.threats || 0) / maxThreats) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="text-sm text-synrgy-muted w-8 text-right">{country.threats || 0}</span>
                  </div>
                </motion.div>
              )
            }) : (
              <div className="text-center text-synrgy-muted py-4">
                <p className="text-sm">No geographic data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-synrgy-surface/30 border border-synrgy-primary/10 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-synrgy-accent/10 rounded-lg flex items-center justify-center">
                <Activity className="w-4 h-4 text-synrgy-accent" />
              </div>
              <h3 className="text-lg font-semibold text-synrgy-text">Recent Activity</h3>
            </div>
            
            {onAskSynrgy && (
              <button
                onClick={() => onAskSynrgy("What recent security activities should I be aware of?")}
                className="p-1.5 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4 text-synrgy-primary" />
              </button>
            )}
          </div>

          <div className="space-y-4">
            {recentEvents.length > 0 ? recentEvents.map((event: any, index: number) => {
              const eventTime = new Date(event.timestamp)
              const timeAgo = `${Math.floor((Date.now() - eventTime.getTime()) / (1000 * 60))} min ago`
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-3 p-3 bg-synrgy-bg-900/30 rounded-lg"
                >
                  <div className="w-2 h-2 rounded-full bg-synrgy-primary" />
                  <div className="flex-1">
                    <p className="text-sm text-synrgy-text">{event.message}</p>
                    <p className="text-xs text-synrgy-muted">{timeAgo} • {event.host}</p>
                  </div>
                  <div className="text-xs px-2 py-1 rounded-full bg-synrgy-primary/20 text-synrgy-primary">
                    Event {event.event_id}
                  </div>
                </motion.div>
              )
            }) : (
              <div className="text-center text-synrgy-muted py-4">
                <p>No recent Windows events found</p>
                <p className="text-xs">Events from the last hour will appear here</p>
              </div>
            )}
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-gradient-to-br from-synrgy-primary/5 to-synrgy-accent/5 border border-synrgy-primary/20 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 bg-synrgy-primary/20 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-synrgy-primary" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">ＳＹＮＲＧＹ Insights</h3>
          </div>

          <div className="space-y-4">
            {dashboardData?.data?.insights?.length > 0 ? (
              dashboardData.data.insights.map((insight: any, index: number) => (
                <div key={index} className="bg-synrgy-surface/50 border border-synrgy-primary/10 rounded-lg p-4">
                  <p className="text-sm text-synrgy-text mb-3">
                    {insight.message}
                  </p>
                  
                  {onAskSynrgy && insight.action && (
                    <button
                      onClick={() => onAskSynrgy(insight.action)}
                      className="w-full btn-primary text-sm"
                    >
                      {insight.button_text || 'Investigate'}
                    </button>
                  )}
                </div>
              ))
            ) : (
              <div className="bg-synrgy-surface/50 border border-synrgy-primary/10 rounded-lg p-4 text-center">
                <p className="text-sm text-synrgy-muted mb-3">
                  ＳＹＮＲＧＹ is analyzing your security data...
                </p>
                
                {onAskSynrgy && (
                  <button
                    onClick={() => onAskSynrgy("Generate security insights from current data")}
                    className="btn-secondary text-sm"
                  >
                    Ask for Insights
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
