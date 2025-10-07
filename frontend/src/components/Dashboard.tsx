import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  AlertTriangle,
  TrendingUp,
  Activity,
  Database,
  Clock,
  Search,
  FileText,
  BarChart3,
  PieChart,
  Zap,
  Users,
  Globe,
  Lock,
  Eye,
  RefreshCw,
  Download,
  Filter,
  Calendar
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, Legend } from 'recharts';

interface DashboardStats {
  total_alerts: number;
  critical_threats: number;
  blocked_attempts: number;
  system_health: number;
  active_investigations: number;
  processed_logs: number;
  query_performance_ms: number;
  uptime_percentage: number;
}

interface AlertTrend {
  timestamp: string;
  alerts: number;
  threats: number;
  blocked: number;
}

interface ThreatCategory {
  name: string;
  count: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface RecentActivity {
  id: string;
  type: 'alert' | 'investigation' | 'report' | 'query';
  title: string;
  timestamp: string;
  severity?: string;
  status: 'active' | 'resolved' | 'investigating';
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_alerts: 1247,
    critical_threats: 23,
    blocked_attempts: 89,
    system_health: 96.4,
    active_investigations: 7,
    processed_logs: 2845692,
    query_performance_ms: 145,
    uptime_percentage: 99.8
  });

  const [alertTrends] = useState<AlertTrend[]>([
    { timestamp: '00:00', alerts: 45, threats: 12, blocked: 8 },
    { timestamp: '04:00', alerts: 32, threats: 8, blocked: 15 },
    { timestamp: '08:00', alerts: 78, threats: 25, blocked: 34 },
    { timestamp: '12:00', alerts: 95, threats: 18, blocked: 28 },
    { timestamp: '16:00', alerts: 124, threats: 35, blocked: 45 },
    { timestamp: '20:00', alerts: 89, threats: 22, blocked: 38 }
  ]);

  const [threatCategories] = useState<ThreatCategory[]>([
    { name: 'Malware', count: 45, severity: 'critical' },
    { name: 'Phishing', count: 32, severity: 'high' },
    { name: 'Brute Force', count: 28, severity: 'medium' },
    { name: 'Anomalous Access', count: 18, severity: 'high' },
    { name: 'Data Exfiltration', count: 12, severity: 'critical' },
    { name: 'Privilege Escalation', count: 8, severity: 'high' }
  ]);

  const [recentActivity] = useState<RecentActivity[]>([
    {
      id: '1',
      type: 'alert',
      title: 'Suspicious login from unusual location',
      timestamp: '2 minutes ago',
      severity: 'high',
      status: 'active'
    },
    {
      id: '2',
      type: 'investigation',
      title: 'Investigating potential data breach',
      timestamp: '15 minutes ago',
      severity: 'critical',
      status: 'investigating'
    },
    {
      id: '3',
      type: 'report',
      title: 'Daily security summary generated',
      timestamp: '1 hour ago',
      status: 'resolved'
    },
    {
      id: '4',
      type: 'query',
      title: 'Analyzed authentication logs',
      timestamp: '2 hours ago',
      status: 'resolved'
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const refreshData = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLastRefresh(new Date());
    setIsLoading(false);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'alert': return <AlertTriangle className="w-4 h-4" />;
      case 'investigation': return <Search className="w-4 h-4" />;
      case 'report': return <FileText className="w-4 h-4" />;
      case 'query': return <Database className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20';
      default: return 'text-space-400 bg-space-500/10 border-space-500/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-red-400 bg-red-500/10';
      case 'investigating': return 'text-yellow-400 bg-yellow-500/10';
      case 'resolved': return 'text-green-400 bg-green-500/10';
      default: return 'text-space-400 bg-space-500/10';
    }
  };

  const COLORS = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyber-darker via-space-950 to-cyber-dark p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Security Dashboard</h1>
            <p className="text-space-400">
              Real-time monitoring and threat intelligence • Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={refreshData}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 rounded-lg text-cyber-accent transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-space-700/50 hover:bg-space-600/50 border border-space-600/50 rounded-lg text-space-300 transition-colors">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              title: 'Total Alerts',
              value: formatNumber(stats.total_alerts),
              change: '+12%',
              icon: <Shield className="w-8 h-8" />,
              color: 'from-blue-500 to-blue-600',
              textColor: 'text-blue-400'
            },
            {
              title: 'Critical Threats',
              value: stats.critical_threats.toString(),
              change: '-3%',
              icon: <AlertTriangle className="w-8 h-8" />,
              color: 'from-red-500 to-red-600',
              textColor: 'text-red-400'
            },
            {
              title: 'Blocked Attempts',
              value: stats.blocked_attempts.toString(),
              change: '+8%',
              icon: <Lock className="w-8 h-8" />,
              color: 'from-green-500 to-green-600',
              textColor: 'text-green-400'
            },
            {
              title: 'System Health',
              value: `${stats.system_health}%`,
              change: '+0.2%',
              icon: <Activity className="w-8 h-8" />,
              color: 'from-cyber-accent to-space-500',
              textColor: 'text-cyber-accent'
            }
          ].map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6 hover:border-space-600/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-space-400 text-sm font-medium">{metric.title}</p>
                  <p className="text-3xl font-bold text-white mt-1">{metric.value}</p>
                  <p className={`text-sm mt-2 ${metric.textColor}`}>
                    {metric.change} from last week
                  </p>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${metric.color} shadow-lg`}>
                  <div className="text-white">
                    {metric.icon}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Alert Trends Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Alert Trends</h3>
              <div className="flex items-center space-x-2 text-sm text-space-400">
                <Calendar className="w-4 h-4" />
                <span>Last 24 hours</span>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={alertTrends}>
                  <defs>
                    <linearGradient id="alertsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="threatsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="timestamp" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: '1px solid #374151', 
                      borderRadius: '8px',
                      color: '#f3f4f6'
                    }} 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="alerts" 
                    stroke="#3b82f6" 
                    fillOpacity={1} 
                    fill="url(#alertsGradient)" 
                    strokeWidth={2}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="threats" 
                    stroke="#ef4444" 
                    fillOpacity={1} 
                    fill="url(#threatsGradient)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Threat Categories */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Threat Categories</h3>
              <PieChart className="w-5 h-5 text-space-400" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={threatCategories}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="count"
                  >
                    {threatCategories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.severity as keyof typeof COLORS]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: '1px solid #374151', 
                      borderRadius: '8px',
                      color: '#f3f4f6'
                    }} 
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2">
              {threatCategories.map((category, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: COLORS[category.severity as keyof typeof COLORS] }}
                    />
                    <span className="text-space-300">{category.name}</span>
                  </div>
                  <span className="text-white font-medium">{category.count}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="lg:col-span-2 bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Recent Activity</h3>
              <button className="flex items-center space-x-1 text-sm text-cyber-accent hover:text-cyber-accent/80 transition-colors">
                <Eye className="w-4 h-4" />
                <span>View All</span>
              </button>
            </div>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-space-800/30 transition-colors">
                  <div className={`p-2 rounded-lg ${getSeverityColor(activity.severity)}`}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1">
                    <p className="text-white font-medium">{activity.title}</p>
                    <p className="text-space-400 text-sm">{activity.timestamp}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* System Performance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6">System Performance</h3>
            <div className="space-y-6">
              {[
                {
                  label: 'Active Investigations',
                  value: stats.active_investigations,
                  icon: <Search className="w-4 h-4" />,
                  color: 'text-yellow-400'
                },
                {
                  label: 'Processed Logs',
                  value: formatNumber(stats.processed_logs),
                  icon: <Database className="w-4 h-4" />,
                  color: 'text-blue-400'
                },
                {
                  label: 'Query Performance',
                  value: `${stats.query_performance_ms}ms`,
                  icon: <Zap className="w-4 h-4" />,
                  color: 'text-green-400'
                },
                {
                  label: 'System Uptime',
                  value: `${stats.uptime_percentage}%`,
                  icon: <TrendingUp className="w-4 h-4" />,
                  color: 'text-cyber-accent'
                }
              ].map((metric, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={metric.color}>
                      {metric.icon}
                    </div>
                    <span className="text-space-300 text-sm">{metric.label}</span>
                  </div>
                  <span className="text-white font-semibold">{metric.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
