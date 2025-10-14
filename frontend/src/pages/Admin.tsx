/**
 * SYNRGY Admin Panel
 * Comprehensive admin interface for connectors, users, audit logs, and system management
 */

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users,
  Settings,
  Shield,
  Server,
  Database,
  Activity,
  Clock,
  Search,
  Plus,
  Edit3,
  Trash2,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Eye,
  Key,
  Globe,
  HardDrive,
  Cpu,
  MemoryStick,
  Network,
  FileText,
  Download,
  Upload,
  UserPlus,
  UserMinus,
  Lock,
  Unlock,
  BarChart3,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/services/api'
import { useAuth } from '@/providers/AuthProvider'

interface Connector {
  id: string
  name: string
  type: 'elasticsearch' | 'splunk' | 'wazuh' | 'syslog' | 'api' | 'custom'
  status: 'connected' | 'disconnected' | 'error' | 'pending'
  config: Record<string, any>
  created_at: string
  last_health_check: string
  health_status: 'healthy' | 'warning' | 'critical'
  metrics: {
    total_events: number
    events_per_second: number
    latency_ms: number
    error_rate: number
  }
}

interface SystemUser {
  id: string
  username: string
  email: string
  full_name: string
  role: 'admin' | 'analyst' | 'viewer' | 'investigator'
  department: string
  status: 'active' | 'inactive' | 'suspended'
  last_login: string
  permissions: string[]
  created_at: string
  login_count: number
}

interface AuditLog {
  id: string
  user_id: string
  user_name: string
  action: string
  resource: string
  details: Record<string, any>
  ip_address: string
  user_agent: string
  timestamp: string
  risk_level: 'low' | 'medium' | 'high' | 'critical'
}

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: number
  active_connections: number
  total_events_processed: number
  events_per_second: number
  error_rate: number
  uptime: string
}

export default function AdminPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'connectors' | 'users' | 'audit' | 'system'>('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedConnector, setSelectedConnector] = useState<Connector | null>(null)

  // Fetch system metrics
  const { data: systemMetrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ['admin-system-metrics'],
    queryFn: async () => {
      const response = await api.get('/api/admin/system/metrics')
      return response.data.data as SystemMetrics
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Fetch connectors
  const { data: connectors = [], isLoading: loadingConnectors } = useQuery({
    queryKey: ['admin-connectors'],
    queryFn: async () => {
      const response = await api.get('/api/admin/connectors')
      return response.data.data as Connector[]
    },
  })

  // Fetch users
  const { data: users = [], isLoading: loadingUsers } = useQuery({
    queryKey: ['admin-users', { search: searchQuery }],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (searchQuery) params.set('search', searchQuery)
      
      const response = await api.get(`/api/admin/users?${params.toString()}`)
      return response.data.data as SystemUser[]
    },
  })

  // Fetch audit logs
  const { data: auditLogs = [], isLoading: loadingAudit } = useQuery({
    queryKey: ['admin-audit-logs'],
    queryFn: async () => {
      const response = await api.get('/api/admin/audit-logs')
      return response.data.data as AuditLog[]
    },
  })

  // Toggle connector status mutation
  const toggleConnectorMutation = useMutation({
    mutationFn: async ({ id, action }: { id: string; action: 'enable' | 'disable' | 'restart' }) => {
      const response = await api.post(`/api/admin/connectors/${id}/${action}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-connectors'] })
      toast.success('Connector status updated')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update connector')
    },
  })

  // Update user status mutation
  const updateUserStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: SystemUser['status'] }) => {
      const response = await api.patch(`/api/admin/users/${id}`, { status })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      toast.success('User status updated')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update user')
    },
  })

  const getConnectorStatusColor = (status: Connector['status']) => {
    switch (status) {
      case 'connected': return 'text-green-400'
      case 'disconnected': return 'text-gray-400'
      case 'error': return 'text-red-400'
      case 'pending': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  const getHealthStatusColor = (status: Connector['health_status']) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'critical': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getRiskLevelColor = (level: AuditLog['risk_level']) => {
    switch (level) {
      case 'low': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'high': return 'text-orange-400'
      case 'critical': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-synrgy-text mb-2">System Administration</h1>
            <p className="text-synrgy-muted">
              Manage connectors, users, audit logs, and system configuration
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-2 bg-synrgy-surface border border-synrgy-primary/20 rounded-lg">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm text-synrgy-text">System Online</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-synrgy-primary/10">
          <nav className="flex space-x-8">
            {[
              { key: 'overview', label: 'Overview', icon: BarChart3 },
              { key: 'connectors', label: 'Data Connectors', icon: Database },
              { key: 'users', label: 'User Management', icon: Users },
              { key: 'audit', label: 'Audit Logs', icon: FileText },
              { key: 'system', label: 'System Config', icon: Settings },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`flex items-center gap-2 px-1 py-3 border-b-2 font-medium text-sm ${
                  activeTab === key
                    ? 'border-synrgy-primary text-synrgy-primary'
                    : 'border-transparent text-synrgy-muted hover:text-synrgy-text'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid gap-6">
            {/* System Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {systemMetrics ? (
                [
                  { label: 'CPU Usage', value: `${systemMetrics.cpu_usage.toFixed(1)}%`, icon: Cpu, color: systemMetrics.cpu_usage > 80 ? 'text-red-400' : 'text-green-400' },
                  { label: 'Memory Usage', value: `${systemMetrics.memory_usage.toFixed(1)}%`, icon: MemoryStick, color: systemMetrics.memory_usage > 85 ? 'text-red-400' : 'text-green-400' },
                  { label: 'Active Connections', value: systemMetrics.active_connections.toLocaleString(), icon: Network, color: 'text-blue-400' },
                  { label: 'Events/sec', value: systemMetrics.events_per_second.toLocaleString(), icon: Activity, color: 'text-synrgy-primary' },
                ].map((metric, index) => (
                  <motion.div
                    key={metric.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                        <metric.icon className="w-4 h-4 text-synrgy-primary" />
                      </div>
                      <h3 className="text-sm font-medium text-synrgy-muted">{metric.label}</h3>
                    </div>
                    <div className={`text-2xl font-bold ${metric.color}`}>{metric.value}</div>
                  </motion.div>
                ))
              ) : (
                <div className="col-span-4 bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
                  <div className="w-8 h-8 border-2 border-synrgy-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-synrgy-muted">Loading system metrics...</p>
                </div>
              )}
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
                <h3 className="font-semibold text-synrgy-text mb-4">Data Connectors</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Active</span>
                    <span className="text-green-400">{connectors.filter(c => c.status === 'connected').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Inactive</span>
                    <span className="text-gray-400">{connectors.filter(c => c.status === 'disconnected').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Errors</span>
                    <span className="text-red-400">{connectors.filter(c => c.status === 'error').length}</span>
                  </div>
                </div>
              </div>

              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
                <h3 className="font-semibold text-synrgy-text mb-4">System Users</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Active</span>
                    <span className="text-green-400">{users.filter(u => u.status === 'active').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Inactive</span>
                    <span className="text-gray-400">{users.filter(u => u.status === 'inactive').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Suspended</span>
                    <span className="text-orange-400">{users.filter(u => u.status === 'suspended').length}</span>
                  </div>
                </div>
              </div>

              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
                <h3 className="font-semibold text-synrgy-text mb-4">Recent Activity</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">High Risk</span>
                    <span className="text-red-400">{auditLogs.filter(l => l.risk_level === 'high' || l.risk_level === 'critical').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Medium Risk</span>
                    <span className="text-yellow-400">{auditLogs.filter(l => l.risk_level === 'medium').length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-synrgy-muted">Low Risk</span>
                    <span className="text-green-400">{auditLogs.filter(l => l.risk_level === 'low').length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Connectors Tab */}
        {activeTab === 'connectors' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-synrgy-text">Data Connectors</h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Connector
              </button>
            </div>

            <div className="grid gap-4">
              {connectors.map((connector) => (
                <motion.div
                  key={connector.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-synrgy-text">{connector.name}</h3>
                        <div className={`px-2 py-1 rounded text-xs ${getConnectorStatusColor(connector.status)}`}>
                          {(connector.status || 'unknown').toUpperCase()}
                        </div>
                        <div className={`px-2 py-1 rounded text-xs ${getHealthStatusColor(connector.health_status)}`}>
                          {(connector.health_status || 'unknown').toUpperCase()}
                        </div>
                        <span className="px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded text-xs">
                          {(connector.type || 'unknown').toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-synrgy-muted">
                        <div>
                          <div className="text-synrgy-text font-medium">{connector.metrics?.total_events?.toLocaleString() || '0'}</div>
                          <div>Total Events</div>
                        </div>
                        <div>
                          <div className="text-synrgy-text font-medium">{connector.metrics?.events_per_second || '0'}/sec</div>
                          <div>Throughput</div>
                        </div>
                        <div>
                          <div className="text-synrgy-text font-medium">{connector.metrics?.latency_ms || '0'}ms</div>
                          <div>Latency</div>
                        </div>
                        <div>
                          <div className="text-synrgy-text font-medium">{((connector.metrics?.error_rate || 0) * 100).toFixed(2)}%</div>
                          <div>Error Rate</div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => toggleConnectorMutation.mutate({ id: connector.id, action: 'restart' })}
                        className="p-2 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                        title="Restart"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          const action = connector.status === 'connected' ? 'disable' : 'enable'
                          toggleConnectorMutation.mutate({ id: connector.id, action })
                        }}
                        className={`p-2 rounded transition-colors ${
                          connector.status === 'connected'
                            ? 'text-synrgy-muted hover:text-red-400 hover:bg-red-400/10'
                            : 'text-synrgy-muted hover:text-green-400 hover:bg-green-400/10'
                        }`}
                        title={connector.status === 'connected' ? 'Disable' : 'Enable'}
                      >
                        {connector.status === 'connected' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => setSelectedConnector(connector)}
                        className="p-2 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-synrgy-text">User Management</h2>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search users..."
                    className="pl-10 pr-4 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                  />
                </div>
                <button
                  className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
                >
                  <UserPlus className="w-4 h-4" />
                  Add User
                </button>
              </div>
            </div>

            <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-synrgy-bg-900/50">
                    <tr className="border-b border-synrgy-primary/10">
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">User</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Role</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Status</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Last Login</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b border-synrgy-primary/5 hover:bg-synrgy-primary/5">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-synrgy-text">{user.full_name}</div>
                            <div className="text-sm text-synrgy-muted">{user.email || 'No email'}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded text-xs">
                            {(user.role || 'user').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs ${
                            user.status === 'active' ? 'text-green-400 bg-green-400/10' :
                            user.status === 'inactive' ? 'text-gray-400 bg-gray-400/10' :
                            'text-orange-400 bg-orange-400/10'
                          }`}>
                            {(user.status || 'unknown').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-synrgy-muted">
                          {new Date(user.last_login).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                const newStatus = user.status === 'active' ? 'suspended' : 'active'
                                updateUserStatusMutation.mutate({ id: user.id, status: newStatus })
                              }}
                              className={`p-1 rounded transition-colors ${
                                user.status === 'active'
                                  ? 'text-synrgy-muted hover:text-orange-400 hover:bg-orange-400/10'
                                  : 'text-synrgy-muted hover:text-green-400 hover:bg-green-400/10'
                              }`}
                              title={user.status === 'active' ? 'Suspend' : 'Activate'}
                            >
                              {user.status === 'active' ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                            </button>
                            <button
                              className="p-1 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                              title="Edit"
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>
                            <button
                              className="p-1 text-synrgy-muted hover:text-red-400 hover:bg-red-400/10 rounded transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Audit Logs Tab */}
        {activeTab === 'audit' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-synrgy-text">Audit Logs</h2>
            
            <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-synrgy-bg-900/50">
                    <tr className="border-b border-synrgy-primary/10">
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Timestamp</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">User</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Action</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">Risk Level</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-synrgy-muted">IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.slice(0, 50).map((log) => (
                      <tr key={log.id} className="border-b border-synrgy-primary/5 hover:bg-synrgy-primary/5">
                        <td className="px-6 py-4 text-sm text-synrgy-muted">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-synrgy-text">
                          {log.user_name}
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-synrgy-text text-sm">{log.action}</div>
                            <div className="text-xs text-synrgy-muted">{log.resource}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs ${getRiskLevelColor(log.risk_level)} ${
                            log.risk_level === 'low' ? 'bg-green-400/10' :
                            log.risk_level === 'medium' ? 'bg-yellow-400/10' :
                            log.risk_level === 'high' ? 'bg-orange-400/10' :
                            'bg-red-400/10'
                          }`}>
                            {(log.risk_level || 'unknown').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-synrgy-muted">
                          {log.ip_address}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* System Config Tab */}
        {activeTab === 'system' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-synrgy-text">System Configuration</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
                <h3 className="font-semibold text-synrgy-text mb-4">Security Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Two-Factor Authentication</span>
                    <button className="w-12 h-6 bg-synrgy-primary rounded-full relative">
                      <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1" />
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Session Timeout (minutes)</span>
                    <input
                      type="number"
                      defaultValue={30}
                      className="w-20 px-2 py-1 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded text-sm text-synrgy-text"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Password Complexity</span>
                    <select className="px-2 py-1 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded text-sm text-synrgy-text">
                      <option>High</option>
                      <option>Medium</option>
                      <option>Low</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
                <h3 className="font-semibold text-synrgy-text mb-4">System Resources</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Auto-scaling</span>
                    <button className="w-12 h-6 bg-synrgy-primary rounded-full relative">
                      <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1" />
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Max Concurrent Users</span>
                    <input
                      type="number"
                      defaultValue={100}
                      className="w-20 px-2 py-1 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded text-sm text-synrgy-text"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-synrgy-muted">Data Retention (days)</span>
                    <input
                      type="number"
                      defaultValue={365}
                      className="w-20 px-2 py-1 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded text-sm text-synrgy-text"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
