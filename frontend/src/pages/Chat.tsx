import React from 'react';
import { motion } from 'framer-motion';
import { ChatWindow } from '../components/ChatWindow';
import { 
  Shield, 
  Activity, 
  Database, 
  Zap,
  AlertTriangle,
  TrendingUp
} from 'lucide-react';

export const Chat: React.FC = () => {
  const handleSendMessage = async (message: string) => {
    console.log('Sending message to SIEM backend:', message);
    // Here you would integrate with your actual SIEM backend
    // For now, the ChatInterface handles mock responses
  };

  return (
    <div className="h-full flex flex-col relative overflow-hidden">
      {/* Header with SIEM Status */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-shrink-0 p-6 bg-cyber-darker/50 border-b border-cyber-gray-700/30"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-white mb-1">
              Conversational SIEM Assistant
            </h1>
            <p className="text-cyber-gray-400">
              Investigate threats and analyze security logs using natural language
            </p>
          </div>
          
          {/* Real-time Status Indicators */}
          <div className="flex items-center space-x-6">
            <StatusCard
              icon={<Database className="w-5 h-5" />}
              label="Elasticsearch"
              status="Connected"
              color="success"
            />
            <StatusCard
              icon={<Shield className="w-5 h-5" />}
              label="Wazuh SIEM"
              status="Active"
              color="success"
            />
            <StatusCard
              icon={<Activity className="w-5 h-5" />}
              label="Processing"
              status="Real-time"
              color="info"
            />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <QuickStat
            icon={<AlertTriangle className="w-4 h-4" />}
            label="Active Alerts"
            value="12"
            trend="+3"
            color="warning"
          />
          <QuickStat
            icon={<Shield className="w-4 h-4" />}
            label="Threats Blocked"
            value="847"
            trend="+23"
            color="success"
          />
          <QuickStat
            icon={<TrendingUp className="w-4 h-4" />}
            label="Events/Min"
            value="1.2k"
            trend="+5%"
            color="info"
          />
          <QuickStat
            icon={<Zap className="w-4 h-4" />}
            label="Response Time"
            value="0.8s"
            trend="-12%"
            color="success"
          />
        </div>
      </motion.div>

      {/* Chat Interface */}
      <div className="flex-1 min-h-0">
        <ChatWindow onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};

interface StatusCardProps {
  icon: React.ReactNode;
  label: string;
  status: string;
  color: 'success' | 'warning' | 'error' | 'info';
}

const StatusCard: React.FC<StatusCardProps> = ({ icon, label, status, color }) => {
  const getColorClasses = () => {
    switch (color) {
      case 'success': return 'text-status-success bg-status-success/10 border-status-success/20';
      case 'warning': return 'text-status-warning bg-status-warning/10 border-status-warning/20';
      case 'error': return 'text-status-error bg-status-error/10 border-status-error/20';
      case 'info': return 'text-cyber-cyan bg-cyber-cyan/10 border-cyber-cyan/20';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10 border-cyber-gray-700/20';
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${getColorClasses()} backdrop-blur-sm`}>
      <div className="flex items-center space-x-2">
        {icon}
        <div>
          <p className="text-xs font-medium opacity-80">{label}</p>
          <p className="text-sm font-bold">{status}</p>
        </div>
      </div>
    </div>
  );
};

interface QuickStatProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  trend: string;
  color: 'success' | 'warning' | 'error' | 'info';
}

const QuickStat: React.FC<QuickStatProps> = ({ icon, label, value, trend, color }) => {
  const getColorClasses = () => {
    switch (color) {
      case 'success': return 'text-status-success';
      case 'warning': return 'text-status-warning';
      case 'error': return 'text-status-error';
      case 'info': return 'text-cyber-cyan';
      default: return 'text-cyber-gray-400';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -1 }}
      className="p-3 bg-cyber-navy/20 border border-cyber-gray-700/30 rounded-lg backdrop-blur-sm"
    >
      <div className="flex items-center justify-between">
        <div className={`p-2 rounded-lg bg-cyber-gray-800/30 ${getColorClasses()}`}>
          {icon}
        </div>
        <span className={`text-xs font-medium ${trend.startsWith('+') ? 'text-status-success' : 'text-status-error'}`}>
          {trend}
        </span>
      </div>
      <div className="mt-2">
        <p className="text-lg font-bold text-white">{value}</p>
        <p className="text-xs text-cyber-gray-400">{label}</p>
      </div>
    </motion.div>
  );
};
