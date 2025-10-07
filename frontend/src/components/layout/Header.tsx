import React from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Search, 
  Bell, 
  Settings, 
  User, 
  Activity,
  Database,
  Zap
} from 'lucide-react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  title = "Conversational SIEM Assistant", 
  subtitle = "Powered by Natural Language Processing"
}) => {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-cyber-dark/90 backdrop-blur-md border-b border-cyber-gray-700/50 relative overflow-hidden"
    >
      {/* Animated Background Lines */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyber-blue/10 to-transparent transform -skew-x-12 translate-x-full animate-scan"></div>
      </div>

      <div className="relative px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Side - Logo and Title */}
          <div className="flex items-center space-x-4">
            {/* ISRO Logo */}
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="flex items-center space-x-3"
            >
              <div className="relative">
                <div className="w-12 h-12 bg-isro-gradient rounded-xl flex items-center justify-center shadow-glow">
                  <Shield className="w-7 h-7 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-status-success rounded-full border-2 border-cyber-dark animate-pulse"></div>
              </div>
              
              <div>
                <h1 className="text-xl font-display font-bold text-white">
                  {title}
                </h1>
                <p className="text-sm text-cyber-gray-400">
                  {subtitle}
                </p>
              </div>
            </motion.div>

            {/* Organization Badge */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-cyber-navy/50 rounded-full border border-isro-accent/30">
              <div className="w-2 h-2 bg-isro-orange rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-cyber-gray-300">ISRO • DoS</span>
            </div>
          </div>

          {/* Center - Status Indicators */}
          <div className="hidden lg:flex items-center space-x-6">
            <StatusIndicator 
              icon={<Database className="w-4 h-4" />}
              label="SIEM Status"
              status="active"
              value="Connected"
            />
            <StatusIndicator 
              icon={<Activity className="w-4 h-4" />}
              label="Threat Level"
              status="warning"
              value="Medium"
            />
            <StatusIndicator 
              icon={<Zap className="w-4 h-4" />}
              label="Processing"
              status="success"
              value="Real-time"
            />
          </div>

          {/* Right Side - Actions */}
          <div className="flex items-center space-x-3">
            {/* Search */}
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 text-cyber-gray-400 hover:text-white hover:bg-cyber-navy/50 rounded-lg transition-all duration-200"
            >
              <Search className="w-5 h-5" />
            </motion.button>

            {/* Notifications */}
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative p-2 text-cyber-gray-400 hover:text-white hover:bg-cyber-navy/50 rounded-lg transition-all duration-200"
            >
              <Bell className="w-5 h-5" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-status-error rounded-full border border-cyber-dark">
                <div className="w-full h-full bg-status-error rounded-full animate-ping"></div>
              </div>
            </motion.button>

            {/* Settings */}
            <motion.button 
              whileHover={{ scale: 1.05, rotate: 90 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 300 }}
              className="p-2 text-cyber-gray-400 hover:text-white hover:bg-cyber-navy/50 rounded-lg transition-all duration-200"
            >
              <Settings className="w-5 h-5" />
            </motion.button>

            {/* User Profile */}
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 p-2 bg-cyber-navy/50 hover:bg-cyber-navy/70 rounded-lg transition-all duration-200"
            >
              <div className="w-8 h-8 bg-isro-gradient rounded-lg flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="hidden md:block text-sm font-medium text-white">Analyst</span>
            </motion.button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

interface StatusIndicatorProps {
  icon: React.ReactNode;
  label: string;
  status: 'success' | 'warning' | 'error' | 'active';
  value: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ icon, label, status, value }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success': return 'text-status-success';
      case 'warning': return 'text-status-warning';
      case 'error': return 'text-status-error';
      case 'active': return 'text-cyber-cyan';
      default: return 'text-cyber-gray-400';
    }
  };

  const getStatusBg = () => {
    switch (status) {
      case 'success': return 'bg-status-success/20';
      case 'warning': return 'bg-status-warning/20';
      case 'error': return 'bg-status-error/20';
      case 'active': return 'bg-cyber-cyan/20';
      default: return 'bg-cyber-gray-800/20';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`p-1 rounded ${getStatusBg()}`}>
        <div className={getStatusColor()}>
          {icon}
        </div>
      </div>
      <div>
        <p className="text-xs text-cyber-gray-400">{label}</p>
        <p className={`text-sm font-medium ${getStatusColor()}`}>{value}</p>
      </div>
    </div>
  );
};