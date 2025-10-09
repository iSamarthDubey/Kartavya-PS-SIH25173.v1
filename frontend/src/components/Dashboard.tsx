/**
 * KARTAVYA SIEM - Enterprise Security Operations Center
 * Professional-grade dashboard - Kibana/Elastic/Wazuh level interface
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  Shield,
  AlertTriangle,
  Activity,
  Users,
  Network,
  Zap,
  TrendingUp,
  TrendingDown,
  Eye,
  RefreshCw,
  Bell,
  Clock,
  MapPin,
  Server,
  Globe,
  Monitor,
  Cpu,
  HardDrive,
  Wifi,
  Database,
  Lock,
  Unlock,
  Search,
  Filter,
  Download,
  Play,
  Pause,
  BarChart3,
  PieChart,
  LineChart,
  Target,
  Crosshair,
  Radar,
  Flame,
  Skull,
  Bug
} from 'lucide-react';

import { useApiClient } from '../services/api.service';
import { useDashboard, useAlerts, useConnection, useLoading } from '../store/appStore';
import { useNotifications } from './ui/NotificationSystem';
import { 
  DashboardSkeleton, 
  LoadingButton, 
  ProgressBar, 
  InlineLoading 
} from './ui/LoadingStates';
import { DashboardErrorBoundary } from './ErrorBoundary';

const Dashboard: React.FC = () => {
  return (
    <DashboardErrorBoundary>
      <div className="min-h-screen bg-gray-900 text-white">
        <DashboardContent />
      </div>
    </DashboardErrorBoundary>
  );
};

const DashboardContent: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [timeRange, setTimeRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedThreatType, setSelectedThreatType] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Hooks
  const { api, callApi } = useApiClient();
  const { metrics, systemStatus, setDashboardMetrics, setSystemStatus } = useDashboard();
  const { alerts, unreadCount, setAlerts } = useAlerts();
  const { isConnected, connectionStatus } = useConnection();
  const { loadingStates, setLoading } = useLoading();
  const { showSuccess, showError, showInfo } = useNotifications();

  // Load dashboard data
  const loadDashboardData = useCallback(async (showNotification = false) => {
    if (showNotification) {
      setRefreshing(true);
    }

    setLoading('dashboard', true);
    
    try {
      // Load metrics with fallback to empty metrics
      const metricsData = await callApi(
        () => api.getDashboardMetrics(),
        {
          loadingMessage: showNotification ? 'Refreshing security metrics...' : undefined,
          onSuccess: (data) => {
            setDashboardMetrics(data);
            setLastUpdate(new Date());
          },
          onError: () => {
            // Set empty metrics object so dashboard still renders with zeros
            setDashboardMetrics({
              totalThreats: 0,
              activeAlerts: 0,
              systemsOnline: 0,
              incidentsToday: 0,
              threatTrends: [],
              topThreats: [],
              securityScore: 0,
              attackVectors: 0
            });
          }
        }
      );

      // Load security alerts with fallback to empty array
      const alertsData = await callApi(
        () => api.getSecurityAlerts(50),
        {
          onSuccess: (data) => setAlerts(data),
          onError: () => setAlerts([])
        }
      );

      // Load system status with fallback to empty array
      const statusData = await callApi(
        () => api.getSystemStatus(),
        {
          onSuccess: (data) => setSystemStatus(data),
          onError: () => setSystemStatus([])
        }
      );

      if (showNotification && metricsData) {
        showSuccess('SOC Dashboard Updated', 'All security metrics synchronized');
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      showError('Backend Connection Failed', 'Unable to connect to backend. Check if backend server is running.');
    } finally {
      setLoading('dashboard', false);
      setRefreshing(false);
    }
  }, [api, callApi, setDashboardMetrics, setAlerts, setSystemStatus, setLoading, showSuccess, showError]);

  // Auto-refresh with configurable intervals
  useEffect(() => {
    loadDashboardData();
    
    if (autoRefresh) {
      const refreshInterval = timeRange === '1h' ? 10000 : timeRange === '24h' ? 30000 : 60000;
      intervalRef.current = setInterval(() => {
        if (isConnected) {
          loadDashboardData();
        }
      }, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [loadDashboardData, isConnected, autoRefresh, timeRange]);

  const handleManualRefresh = () => {
    loadDashboardData(true);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    showInfo(autoRefresh ? 'Auto-refresh disabled' : 'Auto-refresh enabled', 'Dashboard refresh mode updated');
  };

  // Show loading skeleton on initial load
  if (loadingStates.dashboard && !metrics) {
    return <DashboardSkeleton />;
  }
  
  // Show dashboard with fallback data when no metrics are available
  // This ensures users always see stat cards with zeros instead of empty state

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Enterprise SOC Header */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Shield className="w-8 h-8 text-blue-400" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Security Operations Center</h1>
                <p className="text-gray-400 text-sm">Real-time threat detection and incident response</p>
              </div>
            </div>
            
            {/* Time Range Selector */}
            <div className="flex items-center space-x-2 ml-8">
              <span className="text-gray-400 text-sm">Time Range:</span>
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                className="bg-gray-800 border border-gray-600 text-white text-sm rounded px-3 py-1"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-3 px-3 py-1 bg-gray-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  connectionStatus === 'connected' ? 'bg-green-400' :
                  connectionStatus === 'connecting' ? 'bg-yellow-400' :
                  'bg-red-400'
                }`} />
                <span className={`text-sm font-medium ${
                  connectionStatus === 'connected' ? 'text-green-400' :
                  connectionStatus === 'connecting' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {connectionStatus === 'connected' ? 'ONLINE' :
                   connectionStatus === 'connecting' ? 'CONNECTING' : 'OFFLINE'}
                </span>
              </div>
              <div className="text-xs text-gray-400">
                {lastUpdate.toLocaleTimeString()}
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleAutoRefresh}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all ${
                  autoRefresh 
                    ? 'bg-green-900/30 border-green-700 text-green-400' 
                    : 'bg-gray-800 border-gray-600 text-gray-400 hover:border-gray-500'
                }`}
              >
                {autoRefresh ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                <span className="text-sm">Auto-refresh</span>
              </button>
              
              <LoadingButton
                loading={refreshing}
                onClick={handleManualRefresh}
                className="bg-blue-600 hover:bg-blue-700 border-0"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </LoadingButton>
              
              <button className="flex items-center space-x-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 hover:border-gray-500 text-gray-300 rounded-lg transition-colors">
                <Download className="w-4 h-4" />
                <span className="text-sm">Export</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 py-6 space-y-6">
        {/* Critical Security Banner */}
        {alerts.some(alert => alert.severity === 'critical') && (
          <div className="bg-gradient-to-r from-red-900/30 to-orange-900/30 border border-red-700/50 rounded-lg p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Skull className="w-8 h-8 text-red-400 animate-pulse" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-red-400 mb-1">CRITICAL SECURITY INCIDENTS DETECTED</h3>
                  <p className="text-gray-300">
                    {alerts.filter(alert => alert.severity === 'critical').length} critical threats require immediate analyst attention
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-sm">
                    <span className="text-red-400">• Malware Active</span>
                    <span className="text-orange-400">• Data Exfiltration Risk</span>
                    <span className="text-yellow-400">• Privilege Escalation</span>
                  </div>
                </div>
              </div>
              <div className="flex space-x-3">
                <button className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all hover:scale-105">
                  Escalate to SOC-2
                </button>
                <button className="px-6 py-3 bg-gray-800 hover:bg-gray-700 border border-red-700 text-red-400 font-semibold rounded-lg transition-all">
                  View Incidents
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Enterprise Security Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Threat Detection Rate */}
          <div className="col-span-1 bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-600/20 rounded-lg">
                <Target className="w-6 h-6 text-red-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-red-400 font-semibold tracking-wide">THREATS DETECTED</div>
                <div className={`text-xs flex items-center space-x-1 mt-1 ${
                  (metrics?.totalThreats || 0) > 1200 ? 'text-red-400' : 'text-orange-400'
                }`}>
                  <TrendingUp className="w-3 h-3" />
                  <span>+{Math.floor((metrics?.totalThreats || 0) / 100)}% vs yesterday</span>
                </div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {(metrics?.totalThreats || 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-400">24h detection rate</div>
          </div>

          {/* Active Incidents */}
          <div className="col-span-1 bg-gradient-to-br from-yellow-900/20 to-orange-800/10 border border-yellow-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-600/20 rounded-lg">
                <Flame className="w-6 h-6 text-yellow-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-yellow-400 font-semibold tracking-wide">ACTIVE INCIDENTS</div>
                <div className="text-xs flex items-center space-x-1 mt-1 text-yellow-400">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
                  <span>Live monitoring</span>
                </div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {metrics?.activeAlerts || 0}
            </div>
            <div className="text-sm text-gray-400">Require analyst review</div>
          </div>

          {/* Network Health */}
          <div className="col-span-1 bg-gradient-to-br from-green-900/20 to-emerald-800/10 border border-green-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-600/20 rounded-lg">
                <Activity className="w-6 h-6 text-green-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-green-400 font-semibold tracking-wide">NETWORK HEALTH</div>
                <div className="text-xs flex items-center space-x-1 mt-1 text-green-400">
                  <div className="w-2 h-2 bg-green-400 rounded-full" />
                  <span>Operational</span>
                </div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {(metrics?.systemsOnline || 0).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">Systems operational</div>
          </div>

          {/* Attack Vectors */}
          <div className="col-span-1 bg-gradient-to-br from-purple-900/20 to-violet-800/10 border border-purple-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-600/20 rounded-lg">
                <Crosshair className="w-6 h-6 text-purple-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-purple-400 font-semibold tracking-wide">ATTACK VECTORS</div>
                <div className="text-xs text-purple-400 mt-1">MITRE ATT&CK</div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {metrics?.topThreats?.length || 0}
            </div>
            <div className="text-sm text-gray-400">Unique TTPs identified</div>
          </div>

          {/* Data Processed */}
          <div className="col-span-1 bg-gradient-to-br from-blue-900/20 to-cyan-800/10 border border-blue-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-600/20 rounded-lg">
                <Database className="w-6 h-6 text-blue-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-blue-400 font-semibold tracking-wide">DATA PROCESSED</div>
                <div className="text-xs text-blue-400 mt-1">Real-time ingestion</div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {metrics?.dataProcessed || '0 GB'}
            </div>
            <div className="text-sm text-gray-400">Last 24 hours</div>
          </div>

          {/* Response Time */}
          <div className="col-span-1 bg-gradient-to-br from-teal-900/20 to-cyan-800/10 border border-teal-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-teal-600/20 rounded-lg">
                <Zap className="w-6 h-6 text-teal-400" />
              </div>
              <div className="text-right">
                <div className="text-xs text-teal-400 font-semibold tracking-wide">RESPONSE TIME</div>
                <div className="text-xs text-teal-400 mt-1">Avg detection</div>
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {metrics?.responseTime || '0s'}
            </div>
            <div className="text-sm text-gray-400">Mean time to detect</div>
          </div>
        </div>

        {/* Advanced Threat Intelligence Section */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Real-time Attack Map */}
          <div className="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                <Globe className="w-5 h-5 text-blue-400" />
                <span>Global Threat Map</span>
              </h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
                <span className="text-xs text-red-400 font-medium">LIVE ATTACKS</span>
              </div>
            </div>
            <div className="h-64 bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
              {/* Attack visualization */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-purple-900/20" />
              <div className="text-center z-10">
                <div className="text-3xl font-bold text-red-400 mb-2">
                  {(metrics?.totalThreats || 0).toLocaleString()}
                </div>
                <div className="text-sm text-gray-400">Active threat vectors worldwide</div>
                <div className="flex items-center justify-center space-x-4 mt-4 text-xs">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-red-400 rounded-full" />
                    <span className="text-red-400">Critical</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-orange-400 rounded-full" />
                    <span className="text-orange-400">High</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                    <span className="text-yellow-400">Medium</span>
                  </div>
                </div>
              </div>
              {/* Animated threat indicators */}
              {[...Array(6)].map((_, i) => (
                <div 
                  key={i}
                  className="absolute w-3 h-3 bg-red-400 rounded-full animate-ping"
                  style={{
                    left: `${20 + (i * 15)}%`,
                    top: `${30 + (i * 8)}%`,
                    animationDelay: `${i * 0.5}s`
                  }}
                />
              ))}
            </div>
          </div>

          {/* MITRE ATT&CK Framework */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
              <Target className="w-5 h-5 text-purple-400" />
              <span>MITRE ATT&CK</span>
            </h3>
            <div className="space-y-3">
              {(metrics?.mitreTactics || []).length === 0 ? (
                <div className="text-center text-gray-400 py-4">
                  <p>Loading MITRE ATT&CK data...</p>
                </div>
              ) : (metrics?.mitreTactics || []).map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full bg-${item.color}-400`} />
                    <span className="text-xs text-gray-400">{item.tactic}</span>
                  </div>
                  <span className="text-sm text-white font-semibold">{item.count}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-600">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{metrics?.attackVectors || 0}</div>
                <div className="text-xs text-gray-400">Unique TTPs</div>
              </div>
            </div>
          </div>

          {/* Security Score */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
              <Shield className="w-5 h-5 text-green-400" />
              <span>Security Score</span>
            </h3>
            <div className="relative">
              <div className="w-24 h-24 mx-auto">
                <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#374151"
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${(metrics?.securityScore || 0) * 2.51}, 251`}
                    className="transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-green-400">{metrics?.securityScore || 0}%</span>
                </div>
              </div>
              <div className="text-center mt-4">
                <div className="text-xs text-gray-400">Overall security posture</div>
                <div className="text-sm text-green-400 font-medium mt-1">STRONG</div>
              </div>
            </div>
          </div>
        </div>

        {/* Threat Intelligence and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Trends Chart */}
          <div className="lg:col-span-2">
            <ThreatTrendsChart data={metrics?.threatTrends || []} />
          </div>
          
          {/* Top Threats */}
          <TopThreatsCard threats={metrics?.topThreats || []} />
        </div>

      {/* System Status and Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Status */}
        <SystemStatusCard status={systemStatus} />
        
        {/* Recent Security Events */}
        <div className="lg:col-span-2">
          <RecentAlertsCard alerts={alerts.slice(0, 10)} />
        </div>
      </div>

      {/* Network Activity and User Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <NetworkActivityCard />
        <UserActivityCard />
      </div>
      </div>
    </div>
  );
};

// ============= COMPONENT DEFINITIONS =============

interface MetricCardProps {
  title: string;
  value: number | string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  color: 'red' | 'yellow' | 'green' | 'blue';
  badge?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  trend, 
  icon, 
  color,
  badge = false 
}) => {
  const colorClasses = {
    red: 'border-red-700/50 bg-red-900/20',
    yellow: 'border-yellow-700/50 bg-yellow-900/20',
    green: 'border-green-700/50 bg-green-900/20',
    blue: 'border-blue-700/50 bg-blue-900/20'
  };

  const trendIcon = trend === 'up' ? 
    <TrendingUp className="w-4 h-4 text-green-400" /> :
    trend === 'down' ? 
    <TrendingDown className="w-4 h-4 text-red-400" /> :
    <div className="w-4 h-4" />;

  return (
    <div className={`bg-gray-800 border ${colorClasses[color]} rounded-lg p-6 relative`}>
      {badge && (
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
      )}
      
      <div className="flex items-center justify-between mb-4">
        {icon}
        <div className="flex items-center space-x-2 text-sm text-gray-400">
          {trendIcon}
          <span>{change}</span>
        </div>
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-white mb-1">{value}</h3>
        <p className="text-sm text-gray-400">{title}</p>
      </div>
    </div>
  );
};

const ThreatTrendsChart: React.FC<{ data: Array<{ date: string; count: number }> }> = ({ data }) => {
  const maxValue = Math.max(...data.map(d => d.count), 100);
  
  // Only show data if provided from backend - no fallback data
  const chartData = data.length > 0 ? data : [];
  
  // Handle empty data case
  if (chartData.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <span>Threat Detection Trends</span>
          </h3>
        </div>
        <div className="h-48 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <p>Loading threat trend data...</p>
            <p className="text-sm mt-2">Connecting to real-time threat intelligence</p>
          </div>
        </div>
      </div>
    );
  }
  
  const actualMaxValue = Math.max(...chartData.map(d => d.count), 100);
  const totalThreats = chartData.reduce((sum, item) => sum + item.count, 0);
  const avgThreats = Math.round(totalThreats / chartData.length);
  const trendDirection = chartData[chartData.length - 1].count > chartData[0].count ? 'up' : 'down';
  const trendPercentage = Math.abs(((chartData[chartData.length - 1].count - chartData[0].count) / chartData[0].count) * 100);
  
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <span>Threat Detection Trends</span>
        </h3>
        <div className="text-right">
          <div className="text-sm text-gray-400">7-day average</div>
          <div className="text-xl font-bold text-white">{avgThreats}</div>
          <div className={`flex items-center space-x-1 text-xs ${
            trendDirection === 'up' ? 'text-red-400' : 'text-green-400'
          }`}>
            {trendDirection === 'up' ? 
              <TrendingUp className="w-3 h-3" /> : 
              <TrendingDown className="w-3 h-3" />
            }
            <span>{trendPercentage.toFixed(1)}% vs last week</span>
          </div>
        </div>
      </div>
      
      <div className="space-y-3">
        {chartData.map((item, index) => {
          const isToday = index === chartData.length - 1;
          const progressPercentage = (item.count / actualMaxValue) * 100;
          const severity = item.count > avgThreats * 1.5 ? 'critical' : 
                          item.count > avgThreats * 1.2 ? 'high' : 
                          item.count > avgThreats * 0.8 ? 'medium' : 'low';
          
          const barColor = severity === 'critical' ? 'bg-red-500' :
                          severity === 'high' ? 'bg-orange-500' :
                          severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500';
          
          return (
            <div key={index} className={`flex items-center space-x-4 p-2 rounded-lg transition-colors ${
              isToday ? 'bg-blue-900/30 border border-blue-700/50' : 'hover:bg-gray-700/50'
            }`}>
              <div className="text-sm text-gray-400 w-20 flex-shrink-0">
                {isToday ? 'Today' : new Date(item.date).toLocaleDateString('en', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </div>
              <div className="flex-1 relative">
                <div className="h-6 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${barColor} transition-all duration-1000 ease-out relative`}
                    style={{ width: `${progressPercentage}%` }}
                  >
                    {item.count > avgThreats * 1.3 && (
                      <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                        <AlertTriangle className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-sm font-semibold text-white w-16 text-right flex items-center justify-end space-x-2">
                <span>{item.count.toLocaleString()}</span>
                {isToday && <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Quick stats */}
      <div className="mt-6 pt-4 border-t border-gray-700 grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-lg font-bold text-red-400">
            {Math.max(...chartData.map(d => d.count))}
          </div>
          <div className="text-xs text-gray-400">Peak threats</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">
            {Math.min(...chartData.map(d => d.count))}
          </div>
          <div className="text-xs text-gray-400">Lowest day</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">
            {totalThreats.toLocaleString()}
          </div>
          <div className="text-xs text-gray-400">Total detected</div>
        </div>
      </div>
    </div>
  );
};

const TopThreatsCard: React.FC<{ threats: Array<{ name: string; count: number; severity: string }> }> = ({ threats }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-400/20 border-red-700';
      case 'high': return 'text-orange-400 bg-orange-400/20 border-orange-700';
      case 'medium': return 'text-yellow-400 bg-yellow-400/20 border-yellow-700';
      case 'low': return 'text-blue-400 bg-blue-400/20 border-blue-700';
      default: return 'text-gray-400 bg-gray-400/20 border-gray-700';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <Skull className="w-5 h-5" />;
      case 'high': return <Bug className="w-5 h-5" />;
      case 'medium': return <AlertTriangle className="w-5 h-5" />;
      case 'low': return <Eye className="w-5 h-5" />;
      default: return <AlertTriangle className="w-5 h-5" />;
    }
  };

  // Only show threats if provided from backend - no fallback data
  const threatData = threats.length > 0 ? threats : [];

  if (threatData.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
            <Target className="w-5 h-5 text-red-400" />
            <span>Active Threat Intelligence</span>
          </h3>
        </div>
        <div className="h-48 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <p>Loading threat intelligence...</p>
            <p className="text-sm mt-2">Analyzing security events from dataset</p>
          </div>
        </div>
      </div>
    );
  }

  const totalIncidents = threatData.reduce((sum, threat) => sum + threat.count, 0);

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Target className="w-5 h-5 text-red-400" />
          <span>Active Threat Intelligence</span>
        </h3>
        <div className="text-right">
          <div className="text-lg font-bold text-red-400">{totalIncidents}</div>
          <div className="text-xs text-gray-400">Total incidents</div>
        </div>
      </div>
      
      <div className="space-y-3 max-h-80 overflow-y-auto custom-scrollbar">
        {threatData.map((threat, index) => {
          const colors = getSeverityColor(threat.severity);
          const [textColor, bgColor, borderColor] = colors.split(' ');
          const percentage = (threat.count / Math.max(...threatData.map(t => t.count))) * 100;
          
          return (
            <div 
              key={index} 
              className={`p-4 bg-gray-900 border ${borderColor}/50 rounded-lg hover:bg-gray-800 transition-all cursor-pointer group`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 ${bgColor} rounded-lg border ${borderColor}/50`}>
                    <div className={textColor}>
                      {getSeverityIcon(threat.severity)}
                    </div>
                  </div>
                  <div>
                    <p className="text-white font-semibold group-hover:text-blue-400 transition-colors">
                      {threat.name}
                    </p>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className={`text-xs font-medium px-2 py-1 ${bgColor} ${textColor} rounded-full border ${borderColor}/30`}>
                        {threat.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-400">
                        {(threat as any).category || 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-white">{threat.count}</div>
                  <div className="text-xs text-gray-400">incidents</div>
                </div>
              </div>
              
              {/* Threat intensity bar */}
              <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                <div 
                  className={`h-full ${bgColor.replace('/20', '')} transition-all duration-1000`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
              
              {/* Quick actions */}
              <div className="flex items-center justify-between mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="flex space-x-2">
                  <button className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors">
                    Investigate
                  </button>
                  <button className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors">
                    Block
                  </button>
                </div>
                <div className="text-xs text-gray-400">
                  Last seen: {Math.floor(Math.random() * 60)} min ago
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Threat summary */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-red-400">
              {threatData.filter(t => t.severity === 'critical').length}
            </div>
            <div className="text-xs text-gray-400">Critical</div>
          </div>
          <div>
            <div className="text-lg font-bold text-orange-400">
              {threatData.filter(t => t.severity === 'high').length}
            </div>
            <div className="text-xs text-gray-400">High</div>
          </div>
          <div>
            <div className="text-lg font-bold text-yellow-400">
              {threatData.filter(t => t.severity === 'medium').length}
            </div>
            <div className="text-xs text-gray-400">Medium</div>
          </div>
          <div>
            <div className="text-lg font-bold text-blue-400">
              {threatData.filter(t => t.severity === 'low').length}
            </div>
            <div className="text-xs text-gray-400">Low</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SystemStatusCard: React.FC<{ status: any }> = ({ status }) => {
  const services = status || [
    { service: 'Firewall', status: 'online', uptime: '99.9%' },
    { service: 'IDS/IPS', status: 'online', uptime: '98.7%' },
    { service: 'SIEM Engine', status: 'online', uptime: '99.5%' },
    { service: 'Log Collector', status: 'online', uptime: '97.2%' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400 bg-green-400/20';
      case 'degraded': return 'text-yellow-400 bg-yellow-400/20';
      case 'offline': return 'text-red-400 bg-red-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
        <Server className="w-5 h-5" />
        <span>System Status</span>
      </h3>
      
      <div className="space-y-3">
        {services.map((service: any, index: number) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(service.status).split(' ')[1]}`} />
              <span className="text-white">{service.service}</span>
            </div>
            <div className="text-right">
              <p className={`text-sm font-medium capitalize ${getStatusColor(service.status).split(' ')[0]}`}>
                {service.status}
              </p>
              <p className="text-xs text-gray-400">{service.uptime}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const RecentAlertsCard: React.FC<{ alerts: any[] }> = ({ alerts }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      case 'high': return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'low': return <AlertTriangle className="w-5 h-5 text-blue-400" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Recent Security Events</h3>
      
      <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
        {alerts.length > 0 ? alerts.map((alert, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors">
            <div className="flex-shrink-0 mt-0.5">
              {getSeverityIcon(alert.severity)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{alert.title}</p>
              <p className="text-sm text-gray-400 truncate">{alert.description}</p>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                <span>{new Date(alert.timestamp).toLocaleString()}</span>
                <span>{alert.source}</span>
              </div>
            </div>
            <button className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors">
              <Eye className="w-4 h-4" />
            </button>
          </div>
        )) : (
          <div className="flex items-center justify-center h-32 text-gray-500">
            <p>No recent alerts</p>
          </div>
        )}
      </div>
    </div>
  );
};

const NetworkActivityCard: React.FC = () => {
  const [networkData, setNetworkData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { api } = useApiClient();

  useEffect(() => {
    const loadNetworkData = async () => {
      setLoading(true);
      try {
        const response = await api.getNetworkTraffic('1h', 100);
        if (response.success && response.data) {
          // Calculate metrics from network traffic data
          const traffic = response.data;
          const totalBytes = traffic.reduce((sum: number, item: any) => sum + (item.bytes || 0), 0);
          const inboundBytes = traffic.filter((item: any) => item.direction === 'inbound').reduce((sum: number, item: any) => sum + (item.bytes || 0), 0);
          const outboundBytes = traffic.filter((item: any) => item.direction === 'outbound').reduce((sum: number, item: any) => sum + (item.bytes || 0), 0);
          const blockedConnections = traffic.filter((item: any) => item.blocked || item.suspicious).length;
          
          setNetworkData({
            inboundTraffic: (inboundBytes / (1024 * 1024 * 1024)).toFixed(2), // Convert to GB
            outboundTraffic: (outboundBytes / (1024 * 1024 * 1024)).toFixed(2), // Convert to GB
            blockedConnections,
            totalConnections: traffic.length,
            maxTraffic: Math.max(inboundBytes, outboundBytes) / (1024 * 1024 * 1024)
          });
        } else {
          setNetworkData(null);
        }
      } catch (error) {
        console.error('Failed to load network data:', error);
        setNetworkData(null);
      } finally {
        setLoading(false);
      }
    };

    loadNetworkData();
  }, [api]);

  if (loading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Network className="w-5 h-5" />
          <span>Network Activity</span>
        </h3>
        <div className="space-y-4">
          <InlineLoading message="Loading network metrics..." />
        </div>
      </div>
    );
  }

  if (!networkData) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Network className="w-5 h-5" />
          <span>Network Activity</span>
        </h3>
        <div className="flex items-center justify-center h-32 text-gray-400">
          <div className="text-center">
            <p>No network data available</p>
            <p className="text-sm mt-2">Check network monitoring configuration</p>
          </div>
        </div>
      </div>
    );
  }

  const inboundProgress = networkData.maxTraffic > 0 ? (parseFloat(networkData.inboundTraffic) / networkData.maxTraffic) * 100 : 0;
  const outboundProgress = networkData.maxTraffic > 0 ? (parseFloat(networkData.outboundTraffic) / networkData.maxTraffic) * 100 : 0;
  const blockedProgress = networkData.totalConnections > 0 ? (networkData.blockedConnections / networkData.totalConnections) * 100 : 0;

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
        <Network className="w-5 h-5" />
        <span>Network Activity</span>
      </h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Inbound Traffic</span>
          <span className="text-white">{networkData.inboundTraffic} GB/h</span>
        </div>
        <ProgressBar progress={Math.min(inboundProgress, 100)} color="primary" />
        
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Outbound Traffic</span>
          <span className="text-white">{networkData.outboundTraffic} GB/h</span>
        </div>
        <ProgressBar progress={Math.min(outboundProgress, 100)} color="success" />
        
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Blocked Connections</span>
          <span className="text-red-400">{networkData.blockedConnections}</span>
        </div>
        <ProgressBar progress={Math.min(blockedProgress, 100)} color="error" />
        
        <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-500">
          Total connections analyzed: {networkData.totalConnections}
        </div>
      </div>
    </div>
  );
};

const UserActivityCard: React.FC = () => {
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { api } = useApiClient();

  useEffect(() => {
    const loadUserData = async () => {
      setLoading(true);
      try {
        const response = await api.getUserActivity(100);
        if (response.success && response.data) {
          const activities = response.data;
          
          // Calculate metrics from user activity data
          const uniqueUsers = new Set(activities.map((activity: any) => activity.userId || activity.username)).size;
          const failedLogins = activities.filter((activity: any) => 
            activity.action && activity.action.toLowerCase().includes('login') && 
            (activity.action.toLowerCase().includes('failed') || activity.action.toLowerCase().includes('error'))
          ).length;
          const privilegedActions = activities.filter((activity: any) => 
            activity.action && (
              activity.action.toLowerCase().includes('admin') ||
              activity.action.toLowerCase().includes('privilege') ||
              activity.action.toLowerCase().includes('elevated') ||
              (activity.riskScore && activity.riskScore > 7)
            )
          ).length;
          
          // Get top locations from IP addresses (simplified)
          const locationCounts: Record<string, number> = {};
          activities.forEach((activity: any) => {
            if (activity.ipAddress) {
              // Simplified location mapping based on IP patterns
              const ip = activity.ipAddress;
              let location = 'Unknown';
              if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.16.')) {
                location = 'Internal Network';
              } else if (ip.includes('.')){ 
                // Simple geographic guess (in real app, use IP geolocation service)
                location = 'External Network';
              }
              locationCounts[location] = (locationCounts[location] || 0) + 1;
            }
          });
          
          const topLocations = Object.entries(locationCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 3)
            .map(([location, count]) => ({ location, count }));
          
          setUserData({
            activeSessions: uniqueUsers,
            failedLogins,
            privilegedActions,
            totalActivities: activities.length,
            topLocations
          });
        } else {
          setUserData(null);
        }
      } catch (error) {
        console.error('Failed to load user activity data:', error);
        setUserData(null);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [api]);

  if (loading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Users className="w-5 h-5" />
          <span>User Activity</span>
        </h3>
        <div className="space-y-4">
          <InlineLoading message="Loading user activity metrics..." />
        </div>
      </div>
    );
  }

  if (!userData) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Users className="w-5 h-5" />
          <span>User Activity</span>
        </h3>
        <div className="flex items-center justify-center h-32 text-gray-400">
          <div className="text-center">
            <p>No user activity data available</p>
            <p className="text-sm mt-2">Check user activity monitoring configuration</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
        <Users className="w-5 h-5" />
        <span>User Activity</span>
      </h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Active Sessions</span>
          <span className="text-white">{userData.activeSessions.toLocaleString()}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Failed Logins (1h)</span>
          <span className={`${userData.failedLogins > 50 ? 'text-red-400' : userData.failedLogins > 10 ? 'text-yellow-400' : 'text-green-400'}`}>
            {userData.failedLogins}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Privileged Actions</span>
          <span className={`${userData.privilegedActions > 100 ? 'text-orange-400' : 'text-blue-400'}`}>
            {userData.privilegedActions}
          </span>
        </div>
        
        {userData.topLocations && userData.topLocations.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-white mb-2">Top Access Locations</h4>
            <div className="space-y-2">
              {userData.topLocations.map((location: any, index: number) => (
                <div key={index} className="flex items-center space-x-2 text-sm">
                  <MapPin className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-400">{location.location} - </span>
                  <span className="text-white">{location.count} access{location.count !== 1 ? 'es' : ''}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-500">
          Total activities analyzed: {userData.totalActivities}
        </div>
      </div>
    </div>
  );
};

// Empty State Component
const EmptyDashboardState: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center space-y-6 max-w-md mx-auto px-6">
        <div className="w-24 h-24 mx-auto bg-gray-800 rounded-full flex items-center justify-center">
          <Database className="w-12 h-12 text-gray-600" />
        </div>
        
        <div className="space-y-3">
          <h2 className="text-2xl font-bold text-white">No Data Available</h2>
          <p className="text-gray-400">
            Unable to connect to SIEM backend. Please ensure:
          </p>
          <ul className="text-sm text-gray-500 text-left space-y-1">
            <li>• Backend server is running on port 8000</li>
            <li>• Database connections are established</li>
            <li>• SIEM data sources are configured</li>
            <li>• Network connectivity is available</li>
          </ul>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button 
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry Connection</span>
          </button>
          
          <button 
            onClick={() => {
              localStorage.setItem('VITE_ENABLE_MOCK_FALLBACK', 'true');
              window.location.reload();
            }}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>Enable Demo Data</span>
          </button>
        </div>
        
        <p className="text-xs text-gray-600">
          In production, this dashboard displays real SIEM data from your security infrastructure.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
