import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Settings as SettingsIcon,
  Database,
  Globe,
  Shield,
  Monitor,
  Bell,
  User,
  Lock,
  Palette,
  Download,
  Upload,
  RefreshCw,
  Check,
  X,
  AlertTriangle,
  Info,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  Server,
  Zap,
  Clock,
  HardDrive,
  Wifi,
  Activity
} from 'lucide-react';
import { useEnvironment } from '../hooks/useEnvironment';

interface SettingsCategory {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
}

interface SIEMConfig {
  platform: 'elasticsearch' | 'wazuh' | 'mock';
  elasticsearch: {
    url: string;
    username: string;
    password: string;
    index_pattern: string;
    verify_ssl: boolean;
  };
  wazuh: {
    url: string;
    username: string;
    password: string;
    verify_ssl: boolean;
  };
}

interface SystemSettings {
  mode: 'demo' | 'development' | 'production';
  theme: 'dark' | 'light' | 'auto';
  language: string;
  timezone: string;
  auto_refresh: boolean;
  refresh_interval: number;
  notifications_enabled: boolean;
  sound_alerts: boolean;
  max_results: number;
  query_timeout: number;
}

export const Settings: React.FC = () => {
  const { mode, setMode, siemPlatform, setSiemPlatform } = useEnvironment();
  
  const [activeCategory, setActiveCategory] = useState('siem');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showPasswords, setShowPasswords] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'testing'>('disconnected');
  
  const [siemConfig, setSiemConfig] = useState<SIEMConfig>({
    platform: siemPlatform,
    elasticsearch: {
      url: 'https://localhost:9200',
      username: 'elastic',
      password: '',
      index_pattern: 'logs-*',
      verify_ssl: true
    },
    wazuh: {
      url: 'https://localhost:55000',
      username: 'wazuh',
      password: '',
      verify_ssl: true
    }
  });

  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    mode: mode,
    theme: 'dark',
    language: 'en',
    timezone: 'UTC',
    auto_refresh: true,
    refresh_interval: 30,
    notifications_enabled: true,
    sound_alerts: false,
    max_results: 10000,
    query_timeout: 30
  });

  const categories: SettingsCategory[] = [
    {
      id: 'siem',
      title: 'SIEM Configuration',
      icon: <Database className="w-5 h-5" />,
      description: 'Configure connections to Elasticsearch and Wazuh'
    },
    {
      id: 'system',
      title: 'System Settings',
      icon: <SettingsIcon className="w-5 h-5" />,
      description: 'General application preferences and behavior'
    },
    {
      id: 'security',
      title: 'Security',
      icon: <Shield className="w-5 h-5" />,
      description: 'Authentication and access control settings'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      icon: <Bell className="w-5 h-5" />,
      description: 'Alert preferences and notification settings'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: <Palette className="w-5 h-5" />,
      description: 'Theme and display customization options'
    },
    {
      id: 'advanced',
      title: 'Advanced',
      icon: <Monitor className="w-5 h-5" />,
      description: 'Advanced configuration and debugging options'
    }
  ];

  useEffect(() => {
    // Load settings from localStorage
    const savedSiemConfig = localStorage.getItem('siem_config');
    const savedSystemSettings = localStorage.getItem('system_settings');
    
    if (savedSiemConfig) {
      setSiemConfig(JSON.parse(savedSiemConfig));
    }
    
    if (savedSystemSettings) {
      setSystemSettings(JSON.parse(savedSystemSettings));
    }
  }, []);

  const handleSiemConfigChange = (platform: keyof SIEMConfig, field: string, value: any) => {
    if (platform === 'platform') {
      setSiemConfig(prev => ({ ...prev, platform: value }));
      setSiemPlatform(value);
    } else {
      setSiemConfig(prev => ({
        ...prev,
        [platform]: {
          ...prev[platform as keyof Omit<SIEMConfig, 'platform'>],
          [field]: value
        }
      }));
    }
    setHasChanges(true);
  };

  const handleSystemSettingChange = (field: keyof SystemSettings, value: any) => {
    setSystemSettings(prev => ({ ...prev, [field]: value }));
    if (field === 'mode') {
      setMode(value);
    }
    setHasChanges(true);
  };

  const testConnection = async () => {
    setConnectionStatus('testing');
    
    // Simulate connection test
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // In a real implementation, this would make an actual API call
    const success = Math.random() > 0.3; // 70% success rate for demo
    setConnectionStatus(success ? 'connected' : 'disconnected');
    
    return success;
  };

  const saveSettings = async () => {
    setIsSaving(true);
    
    try {
      // Save to localStorage (in real app, this would be an API call)
      localStorage.setItem('siem_config', JSON.stringify(siemConfig));
      localStorage.setItem('system_settings', JSON.stringify(systemSettings));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const resetSettings = () => {
    setSiemConfig({
      platform: 'mock',
      elasticsearch: {
        url: 'https://localhost:9200',
        username: 'elastic',
        password: '',
        index_pattern: 'logs-*',
        verify_ssl: true
      },
      wazuh: {
        url: 'https://localhost:55000',
        username: 'wazuh',
        password: '',
        verify_ssl: true
      }
    });
    
    setSystemSettings({
      mode: 'demo',
      theme: 'dark',
      language: 'en',
      timezone: 'UTC',
      auto_refresh: true,
      refresh_interval: 30,
      notifications_enabled: true,
      sound_alerts: false,
      max_results: 10000,
      query_timeout: 30
    });
    
    setHasChanges(true);
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-400';
      case 'testing': return 'text-yellow-400';
      case 'disconnected': return 'text-red-400';
      default: return 'text-space-400';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'testing': return 'Testing...';
      case 'disconnected': return 'Disconnected';
      default: return 'Unknown';
    }
  };

  const renderSIEMSettings = () => (
    <div className="space-y-6">
      {/* Platform Selection */}
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">SIEM Platform</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { value: 'elasticsearch', label: 'Elasticsearch', description: 'Connect to Elasticsearch cluster' },
            { value: 'wazuh', label: 'Wazuh', description: 'Connect to Wazuh SIEM platform' },
            { value: 'mock', label: 'Demo Mode', description: 'Use mock data for demonstration' }
          ].map((option) => (
            <motion.div
              key={option.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                siemConfig.platform === option.value
                  ? 'border-cyber-accent bg-cyber-accent/10'
                  : 'border-space-600/50 hover:border-space-500/50 bg-space-700/30'
              }`}
              onClick={() => handleSiemConfigChange('platform', '', option.value)}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-white">{option.label}</h4>
                {siemConfig.platform === option.value && <Check className="w-4 h-4 text-cyber-accent" />}
              </div>
              <p className="text-sm text-space-400">{option.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Connection Status */}
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Connection Status</h3>
          <div className={`flex items-center space-x-2 ${getConnectionStatusColor()}`}>
            <Activity className="w-4 h-4" />
            <span className="text-sm font-medium">{getConnectionStatusText()}</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={testConnection}
            disabled={connectionStatus === 'testing' || siemConfig.platform === 'mock'}
            className="px-4 py-2 bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 rounded-lg text-cyber-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {connectionStatus === 'testing' ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Wifi className="w-4 h-4 mr-2" />
                Test Connection
              </>
            )}
          </button>
          
          {siemConfig.platform === 'mock' && (
            <div className="flex items-center space-x-2 text-yellow-400 text-sm">
              <Info className="w-4 h-4" />
              <span>Demo mode uses mock data</span>
            </div>
          )}
        </div>
      </div>

      {/* Elasticsearch Configuration */}
      {siemConfig.platform === 'elasticsearch' && (
        <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">Elasticsearch Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Server URL</label>
              <input
                type="url"
                value={siemConfig.elasticsearch.url}
                onChange={(e) => handleSiemConfigChange('elasticsearch', 'url', e.target.value)}
                className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                placeholder="https://localhost:9200"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Index Pattern</label>
              <input
                type="text"
                value={siemConfig.elasticsearch.index_pattern}
                onChange={(e) => handleSiemConfigChange('elasticsearch', 'index_pattern', e.target.value)}
                className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                placeholder="logs-*"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Username</label>
              <input
                type="text"
                value={siemConfig.elasticsearch.username}
                onChange={(e) => handleSiemConfigChange('elasticsearch', 'username', e.target.value)}
                className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                placeholder="elastic"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPasswords ? 'text' : 'password'}
                  value={siemConfig.elasticsearch.password}
                  onChange={(e) => handleSiemConfigChange('elasticsearch', 'password', e.target.value)}
                  className="w-full px-3 py-2 pr-10 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-space-400 hover:text-space-300"
                >
                  {showPasswords ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={siemConfig.elasticsearch.verify_ssl}
                onChange={(e) => handleSiemConfigChange('elasticsearch', 'verify_ssl', e.target.checked)}
                className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-600/50 rounded focus:ring-cyber-accent focus:ring-1"
              />
              <span className="text-sm text-space-300">Verify SSL Certificate</span>
            </label>
          </div>
        </div>
      )}

      {/* Wazuh Configuration */}
      {siemConfig.platform === 'wazuh' && (
        <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">Wazuh Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Server URL</label>
              <input
                type="url"
                value={siemConfig.wazuh.url}
                onChange={(e) => handleSiemConfigChange('wazuh', 'url', e.target.value)}
                className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                placeholder="https://localhost:55000"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">Username</label>
              <input
                type="text"
                value={siemConfig.wazuh.username}
                onChange={(e) => handleSiemConfigChange('wazuh', 'username', e.target.value)}
                className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                placeholder="wazuh"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-space-300 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPasswords ? 'text' : 'password'}
                  value={siemConfig.wazuh.password}
                  onChange={(e) => handleSiemConfigChange('wazuh', 'password', e.target.value)}
                  className="w-full px-3 py-2 pr-10 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-space-400 hover:text-space-300"
                >
                  {showPasswords ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={siemConfig.wazuh.verify_ssl}
                onChange={(e) => handleSiemConfigChange('wazuh', 'verify_ssl', e.target.checked)}
                className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-600/50 rounded focus:ring-cyber-accent focus:ring-1"
              />
              <span className="text-sm text-space-300">Verify SSL Certificate</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );

  const renderSystemSettings = () => (
    <div className="space-y-6">
      {/* Environment Mode */}
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">Environment Mode</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { value: 'demo', label: 'Demo', description: 'Safe demonstration with mock data' },
            { value: 'development', label: 'Development', description: 'Development environment with debug features' },
            { value: 'production', label: 'Production', description: 'Production environment with full features' }
          ].map((option) => (
            <motion.div
              key={option.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                systemSettings.mode === option.value
                  ? 'border-cyber-accent bg-cyber-accent/10'
                  : 'border-space-600/50 hover:border-space-500/50 bg-space-700/30'
              }`}
              onClick={() => handleSystemSettingChange('mode', option.value)}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-white">{option.label}</h4>
                {systemSettings.mode === option.value && <Check className="w-4 h-4 text-cyber-accent" />}
              </div>
              <p className="text-sm text-space-400">{option.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* General Settings */}
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">General Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-space-300 mb-2">Language</label>
            <select
              value={systemSettings.language}
              onChange={(e) => handleSystemSettingChange('language', e.target.value)}
              className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-space-300 mb-2">Timezone</label>
            <select
              value={systemSettings.timezone}
              onChange={(e) => handleSystemSettingChange('timezone', e.target.value)}
              className="w-full px-3 py-2 bg-space-900/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none"
            >
              <option value="UTC">UTC</option>
              <option value="Asia/Kolkata">Asia/Kolkata</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Europe/London">Europe/London</option>
            </select>
          </div>
        </div>
        
        <div className="mt-6 space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-sm font-medium text-space-300">Auto-refresh dashboard</span>
            <input
              type="checkbox"
              checked={systemSettings.auto_refresh}
              onChange={(e) => handleSystemSettingChange('auto_refresh', e.target.checked)}
              className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-600/50 rounded focus:ring-cyber-accent focus:ring-1"
            />
          </label>
          
          {systemSettings.auto_refresh && (
            <div>
              <label className="block text-sm font-medium text-space-300 mb-2">
                Refresh interval: {systemSettings.refresh_interval} seconds
              </label>
              <input
                type="range"
                min="10"
                max="300"
                step="10"
                value={systemSettings.refresh_interval}
                onChange={(e) => handleSystemSettingChange('refresh_interval', parseInt(e.target.value))}
                className="w-full h-2 bg-space-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
          )}
        </div>
      </div>

      {/* Query Settings */}
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">Query Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-space-300 mb-2">
              Maximum results: {systemSettings.max_results.toLocaleString()}
            </label>
            <input
              type="range"
              min="1000"
              max="100000"
              step="1000"
              value={systemSettings.max_results}
              onChange={(e) => handleSystemSettingChange('max_results', parseInt(e.target.value))}
              className="w-full h-2 bg-space-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-space-300 mb-2">
              Query timeout: {systemSettings.query_timeout} seconds
            </label>
            <input
              type="range"
              min="5"
              max="120"
              step="5"
              value={systemSettings.query_timeout}
              onChange={(e) => handleSystemSettingChange('query_timeout', parseInt(e.target.value))}
              className="w-full h-2 bg-space-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="bg-space-800/30 rounded-lg p-6 border border-space-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-sm font-medium text-space-300">Enable notifications</span>
            <input
              type="checkbox"
              checked={systemSettings.notifications_enabled}
              onChange={(e) => handleSystemSettingChange('notifications_enabled', e.target.checked)}
              className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-600/50 rounded focus:ring-cyber-accent focus:ring-1"
            />
          </label>
          
          <label className="flex items-center justify-between">
            <span className="text-sm font-medium text-space-300">Sound alerts</span>
            <input
              type="checkbox"
              checked={systemSettings.sound_alerts}
              onChange={(e) => handleSystemSettingChange('sound_alerts', e.target.checked)}
              className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-600/50 rounded focus:ring-cyber-accent focus:ring-1"
            />
          </label>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeCategory) {
      case 'siem': return renderSIEMSettings();
      case 'system': return renderSystemSettings();
      case 'notifications': return renderNotificationSettings();
      default: 
        return (
          <div className="text-center py-12">
            <div className="text-space-400 mb-2">
              <SettingsIcon className="w-12 h-12 mx-auto mb-4" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Settings Category</h3>
            <p className="text-space-400">This settings category is coming soon.</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyber-darker via-space-950 to-cyber-dark p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <div className="w-full lg:w-80 space-y-4">
            <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6">
              <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
              <p className="text-space-400 text-sm">Configure your SIEM assistant preferences</p>
            </div>
            
            <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl overflow-hidden">
              <nav className="space-y-1">
                {categories.map((category) => (
                  <motion.button
                    key={category.id}
                    whileHover={{ x: 4 }}
                    onClick={() => setActiveCategory(category.id)}
                    className={`w-full text-left px-6 py-4 transition-all ${
                      activeCategory === category.id
                        ? 'bg-cyber-accent/20 border-r-2 border-cyber-accent text-white'
                        : 'text-space-300 hover:text-white hover:bg-space-800/30'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={activeCategory === category.id ? 'text-cyber-accent' : 'text-space-400'}>
                        {category.icon}
                      </div>
                      <div>
                        <h3 className="font-medium">{category.title}</h3>
                        <p className="text-xs text-space-400 mt-1">{category.description}</p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </nav>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1">
            <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {categories.find(c => c.id === activeCategory)?.title}
                </h2>
                
                <div className="flex items-center space-x-3">
                  {hasChanges && (
                    <div className="flex items-center space-x-2 text-yellow-400 text-sm">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Unsaved changes</span>
                    </div>
                  )}
                  
                  <button
                    onClick={resetSettings}
                    className="px-4 py-2 text-space-400 hover:text-space-300 border border-space-600/50 rounded-lg transition-colors"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </button>
                  
                  <button
                    onClick={saveSettings}
                    disabled={!hasChanges || isSaving}
                    className="px-4 py-2 bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 rounded-lg text-cyber-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSaving ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </button>
                </div>
              </div>
              
              <div className="min-h-[500px]">
                {renderContent()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
