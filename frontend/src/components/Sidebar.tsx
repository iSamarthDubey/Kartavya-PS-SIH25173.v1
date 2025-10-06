import React from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, BarChart3, FileText, Settings } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'chat', label: 'Chat Assistant', icon: MessageCircle },
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <motion.div
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="w-64 bg-cyber-darker/50 backdrop-blur-md border-r border-glass-medium flex flex-col"
    >
      {/* Header */}
      <div className="p-6 border-b border-glass-medium">
        <h1 className="text-xl font-bold neon-text">SIEM Assistant</h1>
        <p className="text-xs text-gray-400">ISRO SIH 2025</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <motion.button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`sidebar-item w-full text-left ${
                  isActive ? 'active' : ''
                }`}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </motion.button>
            );
          })}
        </div>
      </nav>
    </motion.div>
  );
};
