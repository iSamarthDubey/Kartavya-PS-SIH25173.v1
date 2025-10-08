import React from 'react';
import { Activity, AlertTriangle, Shield, TrendingUp, Users, Globe } from 'lucide-react';

interface DashboardProps {
  isConnected: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ isConnected }) => {
  const stats = [
    { label: 'Active Alerts', value: '23', icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10' },
    { label: 'System Health', value: '94%', icon: Activity, color: 'text-green-400', bg: 'bg-green-500/10' },
    { label: 'Threats Blocked', value: '1,247', icon: Shield, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Monitoring Points', value: '158', icon: Globe, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  ];

  const recentAlerts = [
    { id: 1, type: 'Critical', message: 'Multiple failed login attempts from external IP', time: '2 min ago', severity: 'high' },
    { id: 2, type: 'Warning', message: 'Unusual network traffic detected on VLAN 100', time: '15 min ago', severity: 'medium' },
    { id: 3, type: 'Info', message: 'Scheduled maintenance completed successfully', time: '1 hour ago', severity: 'low' },
    { id: 4, type: 'Critical', message: 'Malware signature detected on workstation WS-045', time: '2 hours ago', severity: 'high' },
  ];

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      {!isConnected && (
        <div className="bg-yellow-600/20 border border-yellow-600/30 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <span className="text-yellow-300 font-medium">Demo Dashboard</span>
            <span className="text-gray-300">- Displaying simulated security metrics</span>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Timeline */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-400" />
            Threat Activity (24h)
          </h3>
          <div className="h-48 flex items-end justify-between space-x-2">
            {[65, 45, 78, 89, 67, 123, 95, 76, 54, 89, 108, 87].map((height, i) => (
              <div key={i} className="flex-1 bg-blue-500/20 rounded-t-lg" style={{ height: `${height}%` }}>
                <div className="w-full bg-blue-500 rounded-t-lg" style={{ height: '20%' }}></div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Threats */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2 text-red-400" />
            Top Threat Sources
          </h3>
          <div className="space-y-3">
            {[
              { ip: '192.168.1.45', threats: 23, country: 'Unknown' },
              { ip: '203.45.12.8', threats: 18, country: 'China' },
              { ip: '185.99.11.45', threats: 15, country: 'Russia' },
              { ip: '91.234.567.12', threats: 12, country: 'Germany' },
            ].map((source, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="text-white font-medium">{source.ip}</p>
                  <p className="text-xs text-gray-400">{source.country}</p>
                </div>
                <div className="text-right">
                  <p className="text-red-400 font-bold">{source.threats}</p>
                  <p className="text-xs text-gray-400">threats</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2 text-yellow-400" />
          Recent Security Alerts
        </h3>
        <div className="space-y-3">
          {recentAlerts.map((alert) => (
            <div key={alert.id} className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg border border-gray-600">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  alert.severity === 'high' ? 'bg-red-500' :
                  alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                }`}></div>
                <div>
                  <p className="text-white font-medium">{alert.message}</p>
                  <p className="text-xs text-gray-400">{alert.type} • {alert.time}</p>
                </div>
              </div>
              <button className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors">
                Investigate
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
