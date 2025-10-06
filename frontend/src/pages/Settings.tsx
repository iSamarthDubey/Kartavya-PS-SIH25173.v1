import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Server, Palette, User, RefreshCw, TestTube, CheckCircle, XCircle } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [userRole, setUserRole] = useState<'analyst' | 'admin'>('analyst');
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testResult, setTestResult] = useState('');

  const handleTestConnection = async () => {
    setConnectionStatus('testing');
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock result
      const isSuccess = Math.random() > 0.3; // 70% success rate for demo
      setConnectionStatus(isSuccess ? 'success' : 'error');
      setTestResult(isSuccess 
        ? 'Connection successful! Backend is responding normally.'
        : 'Connection failed. Please check the API URL and ensure the backend is running.'
      );
    } catch (error) {
      setConnectionStatus('error');
      setTestResult('Connection test failed due to network error.');
    }
  };

  const handleThemeToggle = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="h-full flex flex-col"
    >
      {/* Header */}
      <div className="glass-card p-6 mb-6">
        <div className="flex items-center gap-3">
          <Settings className="w-8 h-8 text-cyber-blue" />
          <div>
            <h1 className="text-2xl font-bold neon-text">Settings</h1>
            <p className="text-gray-400">Configure your SIEM Assistant preferences</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        {/* API Configuration */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Server className="w-5 h-5" />
            API Configuration
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Backend API URL</label>
              <input
                type="url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000/api"
                className="cyber-input w-full"
              />
              <p className="text-xs text-gray-400 mt-1">
                Enter the base URL for your SIEM Assistant backend API
              </p>
            </div>

            <div className="flex items-center gap-4">
              <motion.button
                onClick={handleTestConnection}
                disabled={connectionStatus === 'testing'}
                className="cyber-button flex items-center gap-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <TestTube className={`w-4 h-4 ${connectionStatus === 'testing' ? 'animate-spin' : ''}`} />
                {connectionStatus === 'testing' ? 'Testing...' : 'Test Connection'}
              </motion.button>

              {connectionStatus !== 'idle' && (
                <div className="flex items-center gap-2">
                  {connectionStatus === 'success' && (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  )}
                  {connectionStatus === 'error' && (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                  <span className={`text-sm ${
                    connectionStatus === 'success' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {testResult}
                  </span>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Appearance Settings */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Appearance
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Theme</label>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleThemeToggle}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                    theme === 'dark' 
                      ? 'bg-glass-light border-glass-medium' 
                      : 'bg-glass-medium border-glass-light'
                  }`}
                >
                  {theme === 'dark' ? '🌙' : '☀️'}
                  {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">User Role</label>
              <select
                value={userRole}
                onChange={(e) => setUserRole(e.target.value as 'analyst' | 'admin')}
                className="cyber-input w-full"
              >
                <option value="analyst">Security Analyst</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="glass-card p-4 mt-6">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center gap-4">
            <span>SIEM Assistant v1.0.0</span>
            <span>•</span>
            <span>ISRO SIH 2025</span>
            <span>•</span>
            <span>Team Kartavya</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
