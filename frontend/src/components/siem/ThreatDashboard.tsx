import React, { useState, useEffect } from 'react';
import {
  Shield,
  AlertTriangle,
  Activity,
  Zap,
  TrendingUp,
  TrendingDown,
  Globe,
  Server,
  Users,
  Clock,
  Eye,
  FileX,
  Network,
  Lock,
  Wifi,
  HardDrive
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ThreatMetrics {
  totalAlerts: number;
  criticalAlerts: number;
  threatsBlocked: number;
  systemHealth: number;
  lastUpdate: Date;
}

interface SecurityEvent {
  id: string;
  timestamp: Date;
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: string;
  source: string;
  description: string;
  status: 'open' | 'investigating' | 'resolved';
}

interface ThreatDashboardProps {
  isConnected: boolean;
  refreshInterval?: number;
}

const ThreatDashboard: React.FC<ThreatDashboardProps> = ({ 
  isConnected, 
  refreshInterval = 30000 
}) => {
  const [metrics, setMetrics] = useState<ThreatMetrics>({
    totalAlerts: 0,
    criticalAlerts: 0,
    threatsBlocked: 0,
    systemHealth: 100,
    lastUpdate: new Date()
  });

  const [recentEvents, setRecentEvents] = useState<SecurityEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data generators for demo
  const generateMockMetrics = (): ThreatMetrics => ({
    totalAlerts: Math.floor(Math.random() * 50) + 10,
    criticalAlerts: Math.floor(Math.random() * 5) + 1,
    threatsBlocked: Math.floor(Math.random() * 1000) + 500,
    systemHealth: Math.floor(Math.random() * 20) + 80,
    lastUpdate: new Date()
  });

  const generateMockEvents = (): SecurityEvent[] => {
    const eventTypes = [
      'Failed SSH Login', 'Malware Detection', 'Network Intrusion', 
      'Privilege Escalation', 'Suspicious File Access', 'Port Scan',
      'DDoS Attack', 'Data Exfiltration Attempt'
    ];
    
    const sources = [
      '192.168.1.100', '10.0.0.15', '203.45.12.8', 'WS-SEC-01',
      'SRV-DB-02', 'FW-DMZ-01', 'Email Gateway', 'Web Server'
    ];

    return Array.from({ length: 8 }, (_, i) => ({
      id: `evt_${Date.now()}_${i}`,
      timestamp: new Date(Date.now() - Math.random() * 3600000),
      severity: ['critical', 'high', 'medium', 'low'][Math.floor(Math.random() * 4)] as any,
      type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
      description: `Detected suspicious activity requiring immediate attention`,
      status: ['open', 'investigating', 'resolved'][Math.floor(Math.random() * 3)] as any
    }));
  };

  // Chart data
  const threatTrendData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    threats: Math.floor(Math.random() * 50) + 10,
    blocked: Math.floor(Math.random() * 30) + 5,
  }));

  const severityData = [
    { name: 'Critical', value: 12, color: '#ef4444' },
    { name: 'High', value: 28, color: '#f97316' },
    { name: 'Medium', value: 45, color: '#eab308' },
    { name: 'Low', value: 89, color: '#22c55e' },
  ];

  const topThreatsData = [
    { name: 'Failed Logins', count: 234 },
    { name: 'Malware', count: 89 },
    { name: 'Port Scans', count: 156 },
    { name: 'Network Intrusion', count: 67 },
    { name: 'Data Exfiltration', count: 23 },
  ];

  useEffect(() => {
    const fetchData = () => {
      setIsLoading(true);
      
      // Simulate API call
      setTimeout(() => {
        setMetrics(generateMockMetrics());
        setRecentEvents(generateMockEvents());
        setIsLoading(false);
      }, 1000);
    };

    fetchData();
    
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-green-500'
    };
    return colors[severity as keyof typeof colors] || 'bg-gray-500';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'high':
        return <TrendingUp className="w-4 h-4 text-orange-400" />;
      case 'medium':
        return <Activity className="w-4 h-4 text-yellow-400" />;
      default:
        return <Shield className="w-4 h-4 text-green-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      open: 'text-red-400 bg-red-900/20',
      investigating: 'text-yellow-400 bg-yellow-900/20',
      resolved: 'text-green-400 bg-green-900/20'
    };
    return colors[status as keyof typeof colors] || 'text-gray-400 bg-gray-900/20';
  };

  return (
    <div className="space-y-6">
      {/* Header with Refresh Status */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Threat Dashboard</h1>
          <p className="text-gray-400">Real-time security monitoring and analysis</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <Clock className="w-4 h-4" />
            <span>Last updated: {metrics.lastUpdate.toLocaleTimeString()}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`} />
            <span className="text-sm text-gray-300">
              {isConnected ? 'Live Feed' : 'Demo Mode'}
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-800/30 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-red-400">{metrics.criticalAlerts}</div>
              <div className="text-xs text-red-300">Critical Alerts</div>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            +{Math.floor(Math.random() * 3 + 1)} from last hour
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-orange-900/20 to-orange-800/10 border border-orange-800/30 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Shield className="w-6 h-6 text-orange-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-orange-400">{metrics.totalAlerts}</div>
              <div className="text-xs text-orange-300">Total Alerts</div>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            Active monitoring across all systems
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-green-900/20 to-green-800/10 border border-green-800/30 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Zap className="w-6 h-6 text-green-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-400">{metrics.threatsBlocked}</div>
              <div className="text-xs text-green-300">Threats Blocked</div>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            Automatic threat prevention active
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-blue-900/20 to-blue-800/10 border border-blue-800/30 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-400">{metrics.systemHealth}%</div>
              <div className="text-xs text-blue-300">System Health</div>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            All systems operational
          </div>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Trends */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">24-Hour Threat Activity</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={threatTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="hour" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Area
                type="monotone"
                dataKey="threats"
                stackId="1"
                stroke="#EF4444"
                fill="#EF444420"
                name="Threats Detected"
              />
              <Area
                type="monotone"
                dataKey="blocked"
                stackId="1"
                stroke="#22C55E"
                fill="#22C55E20"
                name="Threats Blocked"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Alert Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row - Events and Top Threats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Security Events */}
        <div className="lg:col-span-2 bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Recent Security Events</h3>
            <button className="text-blue-400 hover:text-blue-300 text-sm">View All</button>
          </div>
          
          <div className="space-y-3">
            {recentEvents.map((event) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-4 p-3 bg-gray-900/30 rounded-lg border border-gray-700/50"
              >
                <div className="flex-shrink-0">
                  {getSeverityIcon(event.severity)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-200">{event.type}</span>
                    <div className={`w-2 h-2 rounded-full ${getSeverityColor(event.severity)}`} />
                  </div>
                  <div className="text-xs text-gray-400">{event.description}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {event.source} • {event.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(event.status)}`}>
                  {event.status}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Top Threats */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Top Threat Categories</h3>
          
          <div className="space-y-3">
            {topThreatsData.map((threat, index) => (
              <div key={threat.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-sm text-gray-300">{index + 1}.</div>
                  <div>
                    <div className="text-sm font-medium text-gray-200">{threat.name}</div>
                    <div className="text-xs text-gray-400">{threat.count} incidents</div>
                  </div>
                </div>
                
                <div className="w-16 bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full"
                    style={{ width: `${(threat.count / 250) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-gray-700">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-green-400">97%</div>
                <div className="text-xs text-gray-400">Detection Rate</div>
              </div>
              <div>
                <div className="text-lg font-bold text-blue-400">1.2s</div>
                <div className="text-xs text-gray-400">Avg Response</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        {[
          { name: 'Firewall', status: 'active', icon: Shield },
          { name: 'IDS/IPS', status: 'active', icon: Eye },
          { name: 'Antivirus', status: 'active', icon: FileX },
          { name: 'Network', status: 'active', icon: Network },
          { name: 'Authentication', status: 'warning', icon: Lock },
          { name: 'VPN', status: 'active', icon: Wifi },
          { name: 'Backup', status: 'active', icon: HardDrive },
          { name: 'Monitoring', status: 'active', icon: Activity },
        ].map((system) => (
          <div key={system.name} className="bg-gray-800/30 border border-gray-700 rounded-lg p-3 text-center">
            <system.icon className={`w-5 h-5 mx-auto mb-2 ${
              system.status === 'active' ? 'text-green-400' : 
              system.status === 'warning' ? 'text-yellow-400' : 'text-red-400'
            }`} />
            <div className="text-xs font-medium text-gray-200">{system.name}</div>
            <div className={`text-xs mt-1 ${
              system.status === 'active' ? 'text-green-400' : 
              system.status === 'warning' ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {system.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ThreatDashboard;
