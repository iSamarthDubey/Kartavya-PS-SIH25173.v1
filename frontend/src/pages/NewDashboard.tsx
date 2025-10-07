import React from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  TrendingUp, 
  TrendingDown,
  Eye,
  MapPin,
  Clock,
  Database,
  Zap,
  Users,
  Server,
  Globe,
  Lock
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar } from 'recharts';

// Mock data for SIEM dashboard
const threatLevelData = [
  { name: 'Critical', value: 12, color: '#dc2626' },
  { name: 'High', value: 28, color: '#ea580c' },
  { name: 'Medium', value: 45, color: '#d97706' },
  { name: 'Low', value: 89, color: '#65a30d' },
];

const timelineData = [
  { time: '00:00', threats: 23, blocked: 20, incidents: 3 },
  { time: '04:00', threats: 18, blocked: 15, incidents: 3 },
  { time: '08:00', threats: 45, blocked: 38, incidents: 7 },
  { time: '12:00', threats: 67, blocked: 58, incidents: 9 },
  { time: '16:00', threats: 52, blocked: 45, incidents: 7 },
  { time: '20:00', threats: 38, blocked: 32, incidents: 6 },
];

const topThreats = [
  { name: 'Malware Detection', count: 847, trend: '+12%', severity: 'high' },
  { name: 'Failed Logins', count: 432, trend: '+8%', severity: 'medium' },
  { name: 'Suspicious IPs', count: 267, trend: '-5%', severity: 'high' },
  { name: 'Data Exfiltration', count: 23, trend: '+23%', severity: 'critical' },
  { name: 'Privilege Escalation', count: 15, trend: '+15%', severity: 'critical' },
];

const geographicData = [
  { country: 'India', threats: 234, blocked: 98.5 },
  { country: 'China', threats: 156, blocked: 87.2 },
  { country: 'Russia', threats: 89, blocked: 92.1 },
  { country: 'USA', threats: 67, blocked: 95.5 },
  { country: 'Brazil', threats: 45, blocked: 89.8 },
];

export const Dashboard: React.FC = () => {
  return (
    <div className="p-6 space-y-6 overflow-y-auto scrollbar-thin scrollbar-thumb-cyber-gray-600 scrollbar-track-transparent">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Threat Intelligence Dashboard
          </h1>
          <p className="text-cyber-gray-400">
            Real-time security monitoring and threat analysis • Last updated: {new Date().toLocaleTimeString()}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-isro-gradient rounded-lg text-white font-medium"
          >
            Export Report
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-cyber-navy/50 border border-cyber-gray-700/50 rounded-lg text-white font-medium"
          >
            Refresh
          </motion.button>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Threats"
          value="174"
          change="+12%"
          trend="up"
          icon={<AlertTriangle className="w-6 h-6" />}
          color="error"
        />
        <MetricCard
          title="Threats Blocked"
          value="1,247"
          change="+8%"
          trend="up"
          icon={<Shield className="w-6 h-6" />}
          color="success"
        />
        <MetricCard
          title="System Health"
          value="98.7%"
          change="+0.3%"
          trend="up"
          icon={<Activity className="w-6 h-6" />}
          color="success"
        />
        <MetricCard
          title="Response Time"
          value="0.8s"
          change="-15%"
          trend="down"
          icon={<Zap className="w-6 h-6" />}
          color="success"
        />
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Timeline */}
        <div className="lg:col-span-2">
          <DashboardCard title="Threat Activity Timeline" icon={<TrendingUp className="w-5 h-5" />}>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={timelineData}>
                <defs>
                  <linearGradient id="threatsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="blockedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #475569',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="threats"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fill="url(#threatsGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="blocked"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#blockedGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </DashboardCard>
        </div>

        {/* Threat Distribution */}
        <div>
          <DashboardCard title="Threat Severity Distribution" icon={<AlertTriangle className="w-5 h-5" />}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={threatLevelData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {threatLevelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #475569',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {threatLevelData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm text-cyber-gray-300">{item.name}</span>
                  </div>
                  <span className="text-sm font-bold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </DashboardCard>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Threats */}
        <DashboardCard title="Top Threat Types" icon={<Shield className="w-5 h-5" />}>
          <div className="space-y-4">
            {topThreats.map((threat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-cyber-navy/20 rounded-lg border border-cyber-gray-700/30"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    threat.severity === 'critical' ? 'bg-status-critical' :
                    threat.severity === 'high' ? 'bg-status-high' :
                    threat.severity === 'medium' ? 'bg-status-medium' :
                    'bg-status-low'
                  } animate-pulse`}></div>
                  <div>
                    <p className="text-sm font-medium text-white">{threat.name}</p>
                    <p className="text-xs text-cyber-gray-400">Last 24 hours</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-white">{threat.count}</p>
                  <p className={`text-xs ${
                    threat.trend.startsWith('+') ? 'text-status-error' : 'text-status-success'
                  }`}>
                    {threat.trend}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </DashboardCard>

        {/* Geographic Threats */}
        <DashboardCard title="Geographic Threat Distribution" icon={<Globe className="w-5 h-5" />}>
          <div className="space-y-4">
            {geographicData.map((location, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-cyber-navy/20 rounded-lg border border-cyber-gray-700/30"
              >
                <div className="flex items-center space-x-3">
                  <MapPin className="w-4 h-4 text-cyber-cyan" />
                  <div>
                    <p className="text-sm font-medium text-white">{location.country}</p>
                    <p className="text-xs text-cyber-gray-400">{location.threats} threats detected</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-status-success">{location.blocked}%</p>
                  <p className="text-xs text-cyber-gray-400">blocked</p>
                </div>
              </motion.div>
            ))}
          </div>
        </DashboardCard>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SystemStatusCard
          title="Elasticsearch Cluster"
          status="healthy"
          metrics={[
            { label: 'Nodes', value: '3/3' },
            { label: 'Indices', value: '24' },
            { label: 'Docs', value: '1.2M' }
          ]}
          icon={<Database className="w-5 h-5" />}
        />
        <SystemStatusCard
          title="Wazuh Manager"
          status="healthy"
          metrics={[
            { label: 'Agents', value: '48/50' },
            { label: 'Rules', value: '15.2k' },
            { label: 'Alerts/min', value: '127' }
          ]}
          icon={<Shield className="w-5 h-5" />}
        />
        <SystemStatusCard
          title="Log Processing"
          status="warning"
          metrics={[
            { label: 'Ingestion Rate', value: '2.1k/s' },
            { label: 'Queue Size', value: '15k' },
            { label: 'Lag', value: '2.3s' }
          ]}
          icon={<Activity className="w-5 h-5" />}
        />
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: 'success' | 'warning' | 'error' | 'info';
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, trend, icon, color }) => {
  const getColorClasses = () => {
    switch (color) {
      case 'success': return 'from-status-success/20 to-status-success/5 border-status-success/30 text-status-success';
      case 'warning': return 'from-status-warning/20 to-status-warning/5 border-status-warning/30 text-status-warning';
      case 'error': return 'from-status-error/20 to-status-error/5 border-status-error/30 text-status-error';
      case 'info': return 'from-cyber-cyan/20 to-cyber-cyan/5 border-cyber-cyan/30 text-cyber-cyan';
      default: return 'from-cyber-gray-700/20 to-cyber-gray-700/5 border-cyber-gray-700/30 text-cyber-gray-400';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className={`p-6 bg-gradient-to-br ${getColorClasses()} border rounded-xl backdrop-blur-sm`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-cyber-darker/50`}>
          {icon}
        </div>
        <div className={`flex items-center space-x-1 text-sm ${
          trend === 'up' 
            ? change.startsWith('+') ? 'text-status-success' : 'text-status-error'
            : change.startsWith('-') ? 'text-status-success' : 'text-status-error'
        }`}>
          {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{change}</span>
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold text-white mb-1">{value}</p>
        <p className="text-sm text-cyber-gray-400">{title}</p>
      </div>
    </motion.div>
  );
};

interface DashboardCardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, icon, children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="p-6 bg-cyber-navy/20 border border-cyber-gray-700/30 rounded-xl backdrop-blur-sm"
  >
    <div className="flex items-center space-x-3 mb-4">
      <div className="p-2 bg-cyber-darker/50 rounded-lg text-cyber-cyan">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-white">{title}</h3>
    </div>
    {children}
  </motion.div>
);

interface SystemStatusCardProps {
  title: string;
  status: 'healthy' | 'warning' | 'error';
  metrics: { label: string; value: string }[];
  icon: React.ReactNode;
}

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ title, status, metrics, icon }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return 'text-status-success';
      case 'warning': return 'text-status-warning';
      case 'error': return 'text-status-error';
      default: return 'text-cyber-gray-400';
    }
  };

  const getStatusBg = () => {
    switch (status) {
      case 'healthy': return 'bg-status-success/10 border-status-success/20';
      case 'warning': return 'bg-status-warning/10 border-status-warning/20';
      case 'error': return 'bg-status-error/10 border-status-error/20';
      default: return 'bg-cyber-gray-800/10 border-cyber-gray-700/20';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`p-4 ${getStatusBg()} border rounded-xl backdrop-blur-sm`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`${getStatusColor()}`}>
            {icon}
          </div>
          <h4 className="text-sm font-semibold text-white">{title}</h4>
        </div>
        <div className={`w-3 h-3 rounded-full ${
          status === 'healthy' ? 'bg-status-success' :
          status === 'warning' ? 'bg-status-warning' :
          'bg-status-error'
        } animate-pulse`}></div>
      </div>
      
      <div className="space-y-2">
        {metrics.map((metric, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-cyber-gray-400">{metric.label}</span>
            <span className="text-white font-medium">{metric.value}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};