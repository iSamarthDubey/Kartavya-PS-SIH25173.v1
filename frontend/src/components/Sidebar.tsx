import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, 
  BarChart3, 
  FileText, 
  Settings,
  Shield,
  Activity,
  Database,
  Search,
  AlertTriangle,
  TrendingUp,
  Users,
  History,
  Filter,
  Download,
  Zap
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  description?: string;
}

const navItems: NavItem[] = [
  {
    id: 'chat',
    label: 'Chat Assistant',
    icon: <MessageSquare className="w-5 h-5" />,
    description: 'Natural language queries'
  },
  {
    id: 'dashboard',
    label: 'Threat Dashboard',
    icon: <BarChart3 className="w-5 h-5" />,
    badge: '12',
    description: 'Real-time monitoring'
  },
  {
    id: 'investigation',
    label: 'Investigation',
    icon: <Search className="w-5 h-5" />,
    description: 'Deep dive analysis'
  },
  {
    id: 'alerts',
    label: 'Active Alerts',
    icon: <AlertTriangle className="w-5 h-5" />,
    badge: '7',
    description: 'Critical notifications'
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: <FileText className="w-5 h-5" />,
    description: 'Generated reports'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: <TrendingUp className="w-5 h-5" />,
    description: 'Trend analysis'
  }
];

const secondaryItems: NavItem[] = [
  {
    id: 'history',
    label: 'Query History',
    icon: <History className="w-5 h-5" />,
    description: 'Past investigations'
  },
  {
    id: 'filters',
    label: 'Saved Filters',
    icon: <Filter className="w-5 h-5" />,
    description: 'Custom filters'
  },
  {
    id: 'exports',
    label: 'Exports',
    icon: <Download className="w-5 h-5" />,
    description: 'Download center'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings className="w-5 h-5" />,
    description: 'Configuration'
  }
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  return (
    <motion.aside 
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`bg-cyber-darker/95 backdrop-blur-xl border-r border-cyber-gray-700/50 transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-80'
      } flex flex-col relative overflow-hidden`}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 bg-gradient-to-b from-cyber-blue/20 via-transparent to-cyber-purple/20"></div>
        <div className="grid grid-cols-4 gap-4 p-4">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="aspect-square bg-cyber-cyan/10 rounded"></div>
          ))}
        </div>
      </div>

      {/* Header */}
      <div className="relative p-6 border-b border-cyber-gray-700/30">
        <div className="flex items-center justify-between">
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex items-center space-x-3"
              >
                <div className="w-10 h-10 bg-isro-gradient rounded-xl flex items-center justify-center shadow-glow">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-display font-bold text-white">KARTAVYA</h2>
                  <p className="text-xs text-cyber-gray-400">SIEM Assistant</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 text-cyber-gray-400 hover:text-white hover:bg-cyber-navy/50 rounded-lg transition-all duration-200"
          >
            <Zap className="w-4 h-4" />
          </motion.button>
        </div>

        {/* Status Bar */}
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 flex items-center justify-between text-xs"
            >
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-status-success rounded-full animate-pulse"></div>
                <span className="text-cyber-gray-400">System Online</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="w-3 h-3 text-cyber-cyan" />
                <span className="text-cyber-gray-400">Processing</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-cyber-gray-600 scrollbar-track-transparent">
        <div className="p-4 space-y-2">
          {/* Primary Navigation */}
          <div className="space-y-1">
            <AnimatePresence>
              {!isCollapsed && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs font-medium text-cyber-gray-500 uppercase tracking-wider px-3 py-2"
                >
                  Main Menu
                </motion.p>
              )}
            </AnimatePresence>
            
            {navItems.map((item) => (
              <NavItemComponent
                key={item.id}
                item={item}
                isActive={activeTab === item.id}
                isCollapsed={isCollapsed}
                onClick={() => onTabChange(item.id)}
              />
            ))}
          </div>

          {/* Divider */}
          <div className="border-t border-cyber-gray-700/30 my-6"></div>

          {/* Secondary Navigation */}
          <div className="space-y-1">
            <AnimatePresence>
              {!isCollapsed && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-xs font-medium text-cyber-gray-500 uppercase tracking-wider px-3 py-2"
                >
                  Tools
                </motion.p>
              )}
            </AnimatePresence>
            
            {secondaryItems.map((item) => (
              <NavItemComponent
                key={item.id}
                item={item}
                isActive={activeTab === item.id}
                isCollapsed={isCollapsed}
                onClick={() => onTabChange(item.id)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="relative border-t border-cyber-gray-700/30 p-4">
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              {/* Connection Status */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <Database className="w-3 h-3 text-cyber-cyan" />
                  <span className="text-cyber-gray-400">Elasticsearch</span>
                </div>
                <div className="w-2 h-2 bg-status-success rounded-full animate-pulse"></div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <Shield className="w-3 h-3 text-cyber-purple" />
                  <span className="text-cyber-gray-400">Wazuh SIEM</span>
                </div>
                <div className="w-2 h-2 bg-status-success rounded-full animate-pulse"></div>
              </div>

              {/* Version */}
              <div className="text-xs text-cyber-gray-500 text-center pt-2 border-t border-cyber-gray-700/30">
                v2.1.0 • SIH 2025
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
};

interface NavItemComponentProps {
  item: NavItem;
  isActive: boolean;
  isCollapsed: boolean;
  onClick: () => void;
}

const NavItemComponent: React.FC<NavItemComponentProps> = ({ 
  item, 
  isActive, 
  isCollapsed, 
  onClick 
}) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02, x: 4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        relative w-full flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-200 group
        ${isActive 
          ? 'bg-isro-gradient shadow-glow text-white' 
          : 'text-cyber-gray-400 hover:text-white hover:bg-cyber-navy/50'
        }
      `}
    >
      {/* Active Indicator */}
      {isActive && (
        <motion.div
          layoutId="activeIndicator"
          className="absolute left-0 w-1 h-full bg-cyber-cyan rounded-r-full"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      )}

      {/* Icon */}
      <div className={`flex-shrink-0 ${isActive ? 'text-white' : 'text-cyber-gray-400 group-hover:text-white'}`}>
        {item.icon}
      </div>

      {/* Label and Description */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="flex-1 text-left"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{item.label}</span>
              {item.badge && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`
                    px-2 py-1 text-xs font-bold rounded-full
                    ${isActive 
                      ? 'bg-white/20 text-white' 
                      : 'bg-status-error text-white'
                    }
                  `}
                >
                  {item.badge}
                </motion.span>
              )}
            </div>
            {item.description && (
              <p className={`text-xs ${isActive ? 'text-white/70' : 'text-cyber-gray-500'}`}>
                {item.description}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Collapsed Badge */}
      {isCollapsed && item.badge && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-1 -right-1 w-4 h-4 bg-status-error rounded-full flex items-center justify-center"
        >
          <span className="text-xs font-bold text-white">{item.badge}</span>
        </motion.div>
      )}
    </motion.button>
  );
};
