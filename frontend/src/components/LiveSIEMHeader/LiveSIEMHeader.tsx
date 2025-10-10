/**
 * 🔥 KARTAVYA SIEM - Live SIEM Header with Real-Time Metrics
 * Shows constantly updating metrics to simulate live SIEM environment
 */

import React, { useState, useEffect } from 'react';
import { 
  Shield, Activity, AlertTriangle, TrendingUp, Database, 
  Wifi, WifiOff, Loader2, Zap, Users, Server, Clock,
  Filter, X, Globe, User
} from 'lucide-react';

interface LiveSIEMMetrics {
  timestamp: string;
  totalEvents: number;
  criticalAlerts: number;
  highRiskEntities: number;
  activeThreats: number;
  blockedAttacks: number;
  systemHealth: number;
  responseTime: number;
  detectionRate: number;
  falsePositives: number;
}

interface LiveSIEMHeaderProps {
  backendStatus: 'online' | 'offline' | 'checking';
  conversationId?: string;
  activeFilters?: any[];
  onFilterChange?: (filters: any[]) => void;
  queryStats?: {
    totalEvents: number;
    queryTime: number;
    isLoading?: boolean;
  };
}

const LiveSIEMHeader: React.FC<LiveSIEMHeaderProps> = ({ 
  backendStatus, 
  conversationId, 
  activeFilters = [], 
  onFilterChange,
  queryStats 
}) => {
  const [liveMetrics, setLiveMetrics] = useState<LiveSIEMMetrics | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>(new Date().toLocaleTimeString());
  const [filtersCollapsed, setFiltersCollapsed] = useState<boolean>(false);

  useEffect(() => {
    // Update timestamp every second
    const updateInterval = setInterval(() => {
      setLastUpdate(new Date().toLocaleTimeString());
    }, 1000);

    return () => {
      clearInterval(updateInterval);
    };
  }, []);

  const formatNumber = (num: number | undefined) => {
    return num ? num.toLocaleString() : '0';
  };

  const getHealthColor = (health: number) => {
    if (health >= 95) return 'text-green-400';
    if (health >= 90) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Filter chip helpers
  const getFilterChips = () => {
    const chips: any[] = [];
    
    // Always show time range (default: last 24h)
    chips.push({
      id: 'time-range',
      type: 'time',
      label: 'Last 24 hours',
      value: 'now-24h',
      icon: Clock,
      color: 'blue'
    });

    // Add other active filters
    activeFilters.forEach((filter, index) => {
      if (filter.type === 'ip') {
        chips.push({
          id: `ip-${index}`,
          type: 'entity',
          label: `IP: ${filter.value}`,
          value: filter.value,
          icon: Globe,
          color: 'green'
        });
      } else if (filter.type === 'user') {
        chips.push({
          id: `user-${index}`,
          type: 'entity',
          label: `User: ${filter.value}`,
          value: filter.value,
          icon: User,
          color: 'purple'
        });
      } else if (filter.type === 'event_type') {
        chips.push({
          id: `event-${index}`,
          type: 'field',
          label: `Event: ${filter.value}`,
          value: filter.value,
          icon: Shield,
          color: 'yellow'
        });
      } else if (filter.type === 'severity') {
        chips.push({
          id: `severity-${index}`,
          type: 'severity',
          label: `Severity: ${filter.value}`,
          value: filter.value,
          icon: AlertTriangle,
          color: filter.value === 'high' ? 'red' : filter.value === 'medium' ? 'yellow' : 'green'
        });
      }
    });

    return chips;
  };

  const removeFilter = (chipId: string) => {
    if (chipId === 'time-range' || !onFilterChange) {
      return; // Don't allow removing time range
    }

    // Remove the filter from the active filters
    const newFilters = activeFilters.filter((_, index) => 
      !chipId.includes(`-${index}`)
    );
    onFilterChange(newFilters);
  };

  const getChipStyles = (color: string = 'blue') => {
    const colorMap = {
      blue: 'bg-blue-900/40 text-blue-300 border-blue-700/50',
      green: 'bg-green-900/40 text-green-300 border-green-700/50',
      yellow: 'bg-yellow-900/40 text-yellow-300 border-yellow-700/50',
      red: 'bg-red-900/40 text-red-300 border-red-700/50',
      purple: 'bg-purple-900/40 text-purple-300 border-purple-700/50'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
  };

  const getStatusIndicator = () => {
    switch (backendStatus) {
      case 'online':
        return (
          <div className="flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-green-400" />
            <span className="text-xs text-green-300">API STATUS: Online</span>
          </div>
        );
      case 'offline':
        return (
          <div className="flex items-center space-x-2">
            <WifiOff className="w-4 h-4 text-red-400" />
            <span className="text-xs text-red-300">API STATUS: Offline</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 text-yellow-400 animate-spin" />
            <span className="text-xs text-yellow-300">API STATUS: Checking...</span>
          </div>
        );
    }
  };

  return (
    <div className="border-b border-gray-700 bg-gradient-to-r from-gray-800/80 to-gray-900/80 backdrop-blur-sm">
      {/* Main Header */}
      <div className="px-4 py-2">
        <div className="flex items-center justify-between mb-2">
          {/* KARTAVYA SIEM Branding - Compact */}
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white">KARTAVYA SIEM</h1>
              <p className="text-xs text-gray-400">Threat Intelligence</p>
            </div>
          </div>

          {/* Live Status Indicators - Compact */}
          <div className="flex items-center space-x-3">
            {getStatusIndicator()}
            <div className="flex items-center space-x-1">
              <Activity className="w-3 h-3 text-blue-400 animate-pulse" />
              <span className="text-xs text-blue-300">Live</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3 text-gray-400" />
              <span className="text-xs text-gray-400 font-mono">{lastUpdate.slice(-8)}</span>
            </div>
          </div>
        </div>

        
        {/* Active Filters Section */}
        <div className={`${filtersCollapsed ? 'mt-2 pt-1' : 'mt-3 pt-2'} border-t border-gray-700/50`}>
          <div className={`flex items-center justify-between ${filtersCollapsed ? 'mb-1' : 'mb-2'}`}>
            <div className="flex items-center space-x-1">
              <Filter className={`${filtersCollapsed ? 'w-2.5 h-2.5' : 'w-3 h-3'} text-gray-400`} />
              <span className={`${filtersCollapsed ? 'text-xs' : 'text-xs font-semibold'} text-gray-400 uppercase tracking-wider`}>
                {filtersCollapsed ? 'Filters' : 'Filters'}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Clear All Button */}
              {!filtersCollapsed && activeFilters.length > 0 && onFilterChange && (
                <button
                  onClick={() => onFilterChange([])}
                  className="text-xs text-gray-400 hover:text-gray-300 transition-colors"
                >
                  Clear All
                </button>
              )}
              
              {/* Collapse/Expand Button */}
              <button
                onClick={() => setFiltersCollapsed(!filtersCollapsed)}
                className={`${filtersCollapsed ? 'text-xs' : 'text-xs font-medium'} text-blue-400 hover:text-blue-300 transition-colors`}
                title={filtersCollapsed ? 'Expand filters' : 'Collapse filters'}
              >
                {filtersCollapsed ? 'Expand' : 'Collapse'}
              </button>
            </div>
          </div>

          {/* Filter Chips - Only show when not collapsed */}
          {!filtersCollapsed && (
            <>
              <div className="flex flex-wrap gap-1 mb-2">
                {getFilterChips().map((chip) => (
                  <div
                    key={chip.id}
                    className={`flex items-center space-x-1 px-1.5 py-0.5 rounded border text-xs ${getChipStyles(chip.color)} transition-all hover:opacity-80`}
                  >
                    {chip.icon && <chip.icon className="w-2.5 h-2.5" />}
                    <span className="font-medium">{chip.label}</span>
                    
                    {/* Remove Button */}
                    {chip.id !== 'time-range' && (
                      <button
                        onClick={() => removeFilter(chip.id)}
                        className="ml-1 hover:bg-gray-600 rounded-full p-0.5 transition-colors"
                        title="Remove filter"
                      >
                        <X className="w-2.5 h-2.5" />
                      </button>
                    )}
                  </div>
                ))}
                
                {/* Add Filter Button */}
                <button
                  className="flex items-center space-x-1 px-1.5 py-0.5 rounded border border-dashed border-gray-600 text-xs text-gray-400 hover:text-gray-300 hover:border-gray-500 transition-all"
                  title="Add filter"
                >
                  <Filter className="w-2.5 h-2.5" />
                  <span>Add</span>
                </button>
              </div>

              {/* Query Summary */}
              <div className="text-xs text-gray-500">
                <span>
                  {getFilterChips().length === 1 ? 'Showing all events' : `${getFilterChips().length} filters applied`}
                  {queryStats && (
                    <>
                      {' • '}
                      <span className="text-blue-300">
                        {queryStats.isLoading ? 'Loading...' : 
                         queryStats.totalEvents > 0 ? 
                         `${queryStats.totalEvents.toLocaleString()} events` : 
                         'No events'}
                      </span>
                      {!queryStats.isLoading && queryStats.queryTime > 0 && (
                        <>
                          {' • '}
                          <span className="text-green-300">Query time: {queryStats.queryTime.toFixed(2)}s</span>
                        </>
                      )}
                    </>
                  )}
                </span>
              </div>
            </>
          )}
        </div>
      </div>

    </div>
  );
};

export default LiveSIEMHeader;
