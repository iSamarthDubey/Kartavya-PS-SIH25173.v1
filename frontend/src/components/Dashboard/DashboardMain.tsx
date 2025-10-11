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
import { dashboardApi } from '@/services/api'
import { useAppStore } from '@/stores/appStore'
import { useHybridStore } from '@/stores/hybridStore'
import type { SummaryCard } from '@/types'

interface DashboardMainProps {
  onAskSynrgy?: (query: string) => void
  hybridMode?: boolean
  onWidgetAction?: (widgetId: string, action: string, data?: any) => void
  className?: string
}

// Mock data for demo (in production, this comes from your backend)
const MOCK_SUMMARY_CARDS: SummaryCard[] = [
  {
    title: "Active Alerts",
    value: 42,
    change: { value: -12, trend: 'down', period: 'last hour' },
    status: 'warning',
    color: 'accent'
  },
  {
    title: "Critical Events", 
    value: 8,
    change: { value: 25, trend: 'up', period: 'today' },
    status: 'critical',
    color: 'danger'
  },
  {
    title: "Response Time",
    value: "2.3m",
    change: { value: -8, trend: 'down', period: 'this week' },
    status: 'normal',
    color: 'primary'
  },
  {
    title: "Connected SIEMs",
    value: 3,
    change: { value: 0, trend: 'stable', period: 'today' },
    status: 'normal',
    color: 'primary'
  }
]

const MOCK_THREAT_DATA = [
  { name: '00:00', threats: 12, blocked: 10 },
  { name: '04:00', threats: 19, blocked: 15 },
  { name: '08:00', threats: 25, blocked: 22 },
  { name: '12:00', threats: 31, blocked: 28 },
  { name: '16:00', threats: 18, blocked: 16 },
  { name: '20:00', threats: 14, blocked: 12 },
]

const MOCK_TOP_THREATS = [
  { name: 'Brute Force', value: 45, color: '#FF7A00' },
  { name: 'Malware', value: 23, color: '#00EFFF' },
  { name: 'Phishing', value: 18, color: '#22D3EE' },
  { name: 'DDoS', value: 14, color: '#F97316' }
]

const MOCK_GEO_DATA = [
  { country: 'United States', threats: 45, lat: 39.8283, lng: -98.5795 },
  { country: 'China', threats: 32, lat: 35.8617, lng: 104.1954 },
  { country: 'Russia', threats: 28, lat: 61.5240, lng: 105.3188 },
  { country: 'Brazil', threats: 19, lat: -14.2350, lng: -51.9253 },
]

export default function DashboardMain({ 
  onAskSynrgy, 
  hybridMode = false, 
  onWidgetAction,
  className = '' 
}: DashboardMainProps) {
  const [refreshing, setRefreshing] = useState(false)
  const { systemHealth } = useAppStore()
  const { pinnedWidgets, setHybridMode } = useHybridStore()

  // Fetch dashboard data
  const { data: dashboardData, refetch } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: dashboardApi.getOverview,
    refetchInterval: 30000, // Refresh every 30 seconds
    meta: {
      onError: (error: any) => {
        console.warn('Dashboard data fetch failed, using mock data:', error)
      }
    }
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refetch()
    } finally {
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  const summaryCards = (dashboardData as any)?.data?.summary_cards || MOCK_SUMMARY_CARDS

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
              systemHealth?.health_score === 'excellent' ? 'bg-green-500' :
              systemHealth?.health_score === 'good' ? 'bg-synrgy-accent' :
              systemHealth?.health_score === 'degraded' ? 'bg-yellow-500' :
              'bg-red-500'
            }`} />
            <span className="text-synrgy-muted">
              System {systemHealth?.health_score || 'Unknown'}
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
              <AreaChart data={MOCK_THREAT_DATA}>
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
                  data={MOCK_TOP_THREATS}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {MOCK_TOP_THREATS.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
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
            {MOCK_TOP_THREATS.map((threat) => (
              <div key={threat.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: threat.color }} />
                  <span className="text-synrgy-text">{threat.name}</span>
                </div>
                <span className="text-synrgy-muted">{threat.value}%</span>
              </div>
            ))}
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
            {MOCK_GEO_DATA.map((country, index) => (
              <motion.div
                key={country.country}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-synrgy-accent rounded-full" />
                  <span className="text-sm text-synrgy-text">{country.country}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-synrgy-surface rounded-full h-2">
                    <div 
                      className="h-2 bg-synrgy-accent rounded-full transition-all duration-500"
                      style={{ width: `${(country.threats / 50) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-synrgy-muted w-8 text-right">{country.threats}</span>
                </div>
              </motion.div>
            ))}
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
            {[
              { type: 'alert', message: 'Brute force attack blocked', time: '2 min ago', status: 'resolved' },
              { type: 'warning', message: 'Unusual login pattern detected', time: '15 min ago', status: 'investigating' },
              { type: 'info', message: 'System scan completed', time: '1 hour ago', status: 'completed' },
              { type: 'alert', message: 'Malware signature updated', time: '2 hours ago', status: 'completed' },
            ].map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-3 p-3 bg-synrgy-bg-900/30 rounded-lg"
              >
                <div className={`w-2 h-2 rounded-full ${
                  activity.type === 'alert' ? 'bg-red-500' :
                  activity.type === 'warning' ? 'bg-synrgy-accent' :
                  'bg-synrgy-primary'
                }`} />
                <div className="flex-1">
                  <p className="text-sm text-synrgy-text">{activity.message}</p>
                  <p className="text-xs text-synrgy-muted">{activity.time}</p>
                </div>
                <div className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'resolved' ? 'bg-green-500/20 text-green-400' :
                  activity.status === 'investigating' ? 'bg-synrgy-accent/20 text-synrgy-accent' :
                  'bg-synrgy-primary/20 text-synrgy-primary'
                }`}>
                  {activity.status}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-gradient-to-br from-synrgy-primary/5 to-synrgy-accent/5 border border-synrgy-primary/20 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 bg-synrgy-primary/20 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-synrgy-primary" />
            </div>
            <h3 className="text-lg font-semibold text-synrgy-text">SYNRGY Insights</h3>
          </div>

          <div className="space-y-4">
            <div className="bg-synrgy-surface/50 border border-synrgy-primary/10 rounded-lg p-4">
              <p className="text-sm text-synrgy-text mb-3">
                I've detected unusual authentication patterns from 3 IP addresses. 
                Would you like me to investigate?
              </p>
              
              {onAskSynrgy && (
                <button
                  onClick={() => onAskSynrgy("Investigate the unusual authentication patterns you detected")}
                  className="w-full btn-primary text-sm"
                >
                  Investigate Now
                </button>
              )}
            </div>

            <div className="bg-synrgy-surface/50 border border-synrgy-primary/10 rounded-lg p-4">
              <p className="text-sm text-synrgy-text mb-3">
                Your threat response time has improved by 23% this week.
              </p>
              
              {onAskSynrgy && (
                <button
                  onClick={() => onAskSynrgy("Show me details about threat response time improvements")}
                  className="w-full btn-secondary text-sm"
                >
                  View Details
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
