import React, { useState } from 'react';
import { Settings, Database, Users, Shield, Server, Activity } from 'lucide-react';

interface AdminPanelProps {
  isConnected: boolean;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ isConnected }) => {
  const [activeSection, setActiveSection] = useState('system');

  const systemStats = [
    { label: 'SIEM Connection', value: isConnected ? 'Connected' : 'Disconnected', status: isConnected ? 'healthy' : 'warning' },
    { label: 'Query Processing', value: '247ms avg', status: 'healthy' },
    { label: 'Memory Usage', value: '180MB', status: 'healthy' },
    { label: 'Active Sessions', value: '12', status: 'healthy' },
  ];

  const configOptions = [
    { key: 'siem_platform', label: 'SIEM Platform', value: 'Elasticsearch', type: 'select', options: ['Elasticsearch', 'Wazuh', 'Mock'] },
    { key: 'max_query_time', label: 'Max Query Time (ms)', value: '30000', type: 'number' },
    { key: 'enable_debug', label: 'Debug Mode', value: 'false', type: 'boolean' },
    { key: 'rate_limit', label: 'Rate Limit (req/min)', value: '100', type: 'number' },
  ];

  const renderSystemStatus = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemStats.map((stat, index) => (
          <div key={index} className="bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">{stat.label}</span>
              <div className={`w-3 h-3 rounded-full ${
                stat.status === 'healthy' ? 'bg-green-500' :
                stat.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
            </div>
            <p className="text-lg font-semibold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-gray-700/50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4">System Configuration</h4>
        <div className="space-y-4">
          {configOptions.map((option) => (
            <div key={option.key} className="flex items-center justify-between">
              <label className="text-sm text-gray-300">{option.label}</label>
              {option.type === 'select' ? (
                <select className="bg-gray-600 border border-gray-500 rounded px-3 py-1 text-white text-sm">
                  {option.options?.map((opt) => (
                    <option key={opt} value={opt} selected={opt === option.value}>{opt}</option>
                  ))}
                </select>
              ) : option.type === 'boolean' ? (
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked={option.value === 'true'} />
                  <div className="relative w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              ) : (
                <input
                  type={option.type}
                  defaultValue={option.value}
                  className="bg-gray-600 border border-gray-500 rounded px-3 py-1 text-white text-sm w-24"
                />
              )}
            </div>
          ))}
        </div>
        <button className="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
          Save Configuration
        </button>
      </div>
    </div>
  );

  const renderUserManagement = () => (
    <div className="bg-gray-700/50 rounded-lg p-6">
      <h4 className="text-lg font-semibold text-white mb-4">User Management</h4>
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-600/50 rounded-lg">
          <div>
            <p className="text-white font-medium">ISRO Analyst</p>
            <p className="text-sm text-gray-400">Security Analyst • Level 2 Clearance</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Active</span>
            <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors">
              Edit
            </button>
          </div>
        </div>
        <div className="flex items-center justify-between p-4 bg-gray-600/50 rounded-lg">
          <div>
            <p className="text-white font-medium">Admin User</p>
            <p className="text-sm text-gray-400">System Administrator • Full Access</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Active</span>
            <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors">
              Edit
            </button>
          </div>
        </div>
      </div>
      <button className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
        Add New User
      </button>
    </div>
  );

  const sections = [
    { id: 'system', label: 'System Status', icon: Server, component: renderSystemStatus },
    { id: 'users', label: 'User Management', icon: Users, component: renderUserManagement },
  ];

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="flex space-x-1 bg-gray-700/30 p-1 rounded-lg">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              activeSection === section.id
                ? 'bg-gray-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            <section.icon className="w-4 h-4" />
            <span>{section.label}</span>
          </button>
        ))}
      </div>

      {/* Active Section Content */}
      <div>
        {sections.find(s => s.id === activeSection)?.component()}
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2 text-purple-400" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors">
            <Database className="w-8 h-8 text-blue-400 mb-2" />
            <span className="text-sm text-white">Test SIEM Connection</span>
          </button>
          <button className="flex flex-col items-center p-4 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors">
            <Shield className="w-8 h-8 text-green-400 mb-2" />
            <span className="text-sm text-white">Refresh Security Rules</span>
          </button>
          <button className="flex flex-col items-center p-4 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors">
            <Activity className="w-8 h-8 text-yellow-400 mb-2" />
            <span className="text-sm text-white">View System Logs</span>
          </button>
          <button className="flex flex-col items-center p-4 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors">
            <Settings className="w-8 h-8 text-purple-400 mb-2" />
            <span className="text-sm text-white">Export Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
