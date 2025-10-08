import React, { useState, useEffect } from 'react';
import { MessageSquare, Activity, FileText, Settings, LogOut, Zap, Shield, Database, Search } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import Reports from './components/Reports';
import AdminPanel from './components/AdminPanel';
import './App.css';

interface User {
  name: string;
  role: string;
  clearance: string;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [isConnected, setIsConnected] = useState(false);
  const [user, setUser] = useState<User>({ name: 'ISRO Analyst', role: 'Security Analyst', clearance: 'Level 2' });

  // Simulate connection to backend
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setIsConnected(true);
        }
      } catch (error) {
        console.log('Backend not connected, using demo mode');
        setIsConnected(false);
      }
    };
    checkConnection();
  }, []);

  const tabs = [
    { id: 'chat', label: 'SIEM Assistant', icon: MessageSquare, color: 'text-blue-400' },
    { id: 'dashboard', label: 'Threat Dashboard', icon: Activity, color: 'text-green-400' },
    { id: 'reports', label: 'Reports', icon: FileText, color: 'text-yellow-400' },
    { id: 'admin', label: 'Admin', icon: Settings, color: 'text-purple-400' }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface isConnected={isConnected} />;
      case 'dashboard':
        return <Dashboard isConnected={isConnected} />;
      case 'reports':
        return <Reports isConnected={isConnected} />;
      case 'admin':
        return <AdminPanel isConnected={isConnected} />;
      default:
        return <ChatInterface isConnected={isConnected} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Kartavya SIEM</h1>
              <p className="text-sm text-gray-400">Conversational Assistant</p>
            </div>
          </div>
          
          {/* ISRO Badge */}
          <div className="bg-orange-600/20 border border-orange-600/30 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold text-orange-300">ISRO - Department of Space</span>
            </div>
            <p className="text-xs text-gray-400">Mission-Critical Security Operations</p>
          </div>
        </div>

        {/* Connection Status */}
        <div className="px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`}></div>
              <span className="text-sm text-gray-300">
                {isConnected ? 'Live SIEM Connected' : 'Demo Mode Active'}
              </span>
            </div>
            <Database className={`w-4 h-4 ${isConnected ? 'text-green-400' : 'text-yellow-400'}`} />
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 px-6 py-4">
          <div className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gray-700 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? tab.color : 'text-gray-400'}`} />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* User Info & Logout */}
        <div className="p-6 border-t border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm font-semibold text-white">{user.name}</p>
              <p className="text-xs text-gray-400">{user.role}</p>
              <p className="text-xs text-blue-400">{user.clearance}</p>
            </div>
            <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-gray-700/50 rounded-lg p-2 text-center">
              <div className="text-blue-400 font-bold">23</div>
              <div className="text-gray-400">Active Alerts</div>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-2 text-center">
              <div className="text-green-400 font-bold">94%</div>
              <div className="text-gray-400">System Health</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white capitalize">
                {tabs.find(t => t.id === activeTab)?.label}
              </h2>
              <p className="text-sm text-gray-400">
                {activeTab === 'chat' && 'Ask questions in natural language'}
                {activeTab === 'dashboard' && 'Real-time threat monitoring'}
                {activeTab === 'reports' && 'Generate security reports'}
                {activeTab === 'admin' && 'System configuration'}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Performance Indicator */}
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-gray-300">Response: 247ms</span>
              </div>
              
              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Quick search..."
                  className="bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-6 overflow-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default App;
