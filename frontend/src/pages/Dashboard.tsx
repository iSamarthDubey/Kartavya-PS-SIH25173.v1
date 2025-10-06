import React from 'react';
import { motion } from 'framer-motion';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { RefreshCw, AlertTriangle, Shield, Users, Activity } from 'lucide-react';

const COLORS = ['#00f0ff', '#7a00ff', '#ff0080', '#00ff80'];

export const Dashboard: React.FC = () => {
  const [isLoading, setIsLoading] = React.useState(false);

  // Mock data
  const metrics = {
    failedLogins: 45,
    activeAlerts: 23,
    topIPs: 12,
    malwareEvents: 8,
  };

  const loginTrends = [
    { time: '00:00', count: 5 },
    { time: '04:00', count: 8 },
    { time: '08:00', count: 15 },
    { time: '12:00', count: 22 },
    { time: '16:00', count: 18 },
    { time: '20:00', count: 12 },
  ];

  const threatSources = [
    { source: 'Windows', count: 35 },
    { source: 'Linux', count: 28 },
    { source: 'Network', count: 20 },
    { source: 'Firewall', count: 15 },
  ];

  const severityDistribution = [
    { severity: 'Critical', count: 5 },
    { severity: 'High', count: 12 },
    { severity: 'Medium', count: 25 },
    { severity: 'Low', count: 40 },
  ];

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  const MetricCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
  }> = ({ title, value, icon }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="metric-card"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-xl bg-glass-light">
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-sm text-gray-400">{title}</div>
    </motion.div>
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="h-full flex flex-col"
    >
      {/* Header */}
      <div className="glass-card p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold neon-text mb-2">Security Dashboard</h1>
            <p className="text-gray-400">Real-time security metrics and threat intelligence</p>
          </div>
          <motion.button
            onClick={handleRefresh}
            disabled={isLoading}
            className="cyber-button flex items-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Data
          </motion.button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <MetricCard
          title="Failed Logins"
          value={metrics.failedLogins}
          icon={<AlertTriangle className="w-6 h-6 text-red-400" />}
        />
        <MetricCard
          title="Active Alerts"
          value={metrics.activeAlerts}
          icon={<Shield className="w-6 h-6 text-orange-400" />}
        />
        <MetricCard
          title="Top IPs"
          value={metrics.topIPs}
          icon={<Users className="w-6 h-6 text-blue-400" />}
        />
        <MetricCard
          title="Malware Events"
          value={metrics.malwareEvents}
          icon={<Activity className="w-6 h-6 text-purple-400" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        {/* Login Trends */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold mb-4">Login Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={loginTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(11, 15, 25, 0.9)', 
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '8px'
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="#00f0ff" 
                strokeWidth={2}
                dot={{ fill: '#00f0ff', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Threat Sources */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold mb-4">Threat Sources</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={threatSources}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="source" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(11, 15, 25, 0.9)', 
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="count" fill="#7a00ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Severity Distribution */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="chart-container lg:col-span-2"
        >
          <h3 className="text-lg font-semibold mb-4">Alert Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {severityDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(11, 15, 25, 0.9)', 
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '8px'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </motion.div>
  );
};
