/**
 * KARTAVYA SIEM - ContextStrip Component
 * Shows active filters (time range, event types, resolved entities) per blueprint
 */

import React, { useState } from 'react';
import { X, Calendar, Filter, Clock, User, Shield, Globe, AlertTriangle } from 'lucide-react';

interface FilterChip {
  id: string;
  type: 'time' | 'entity' | 'field' | 'severity';
  label: string;
  value: string;
  icon?: React.ElementType;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

interface ContextStripProps {
  filters: any[];
  onFilterChange: (filters: any[]) => void;
  queryStats?: {
    totalEvents: number;
    queryTime: number;
    isLoading?: boolean;
  };
}

const ContextStrip: React.FC<ContextStripProps> = ({ filters, onFilterChange, queryStats }) => {
  const [showDatePicker, setShowDatePicker] = useState(false);

  // Convert generic filters to filter chips for display
  const getFilterChips = (): FilterChip[] => {
    const chips: FilterChip[] = [];
    
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
    filters.forEach((filter, index) => {
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
    if (chipId === 'time-range') {
      // Don't allow removing time range, but could open date picker
      setShowDatePicker(true);
      return;
    }

    // Remove the filter from the active filters
    const newFilters = filters.filter((_, index) => 
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

  const filterChips = getFilterChips();

  if (filterChips.length === 0) {
    return null;
  }

  return (
    <div className="border-b border-gray-700 bg-gray-800/50">
      <div className="p-3">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-xs font-semibold text-gray-400">ACTIVE FILTERS</span>
          </div>
          
          {/* Clear All Button */}
          {filters.length > 0 && (
            <button
              onClick={() => onFilterChange([])}
              className="text-xs text-gray-400 hover:text-gray-300 transition-colors"
            >
              Clear All
            </button>
          )}
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-2">
          {filterChips.map((chip) => (
            <div
              key={chip.id}
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg border text-xs ${getChipStyles(chip.color)} transition-all hover:opacity-80`}
            >
              {chip.icon && <chip.icon className="w-3 h-3" />}
              <span className="font-medium">{chip.label}</span>
              
              {/* Remove Button */}
              <button
                onClick={() => removeFilter(chip.id)}
                className="ml-1 hover:bg-gray-600 rounded-full p-0.5 transition-colors"
                title={chip.id === 'time-range' ? 'Change time range' : 'Remove filter'}
              >
                <X className="w-2.5 h-2.5" />
              </button>
            </div>
          ))}
          
          {/* Add Filter Button */}
          <button
            className="flex items-center space-x-1 px-2 py-1 rounded-lg border border-dashed border-gray-600 text-xs text-gray-400 hover:text-gray-300 hover:border-gray-500 transition-all"
            title="Add filter"
          >
            <Filter className="w-3 h-3" />
            <span>Add</span>
          </button>
        </div>

        {/* Quick Time Range Options */}
        {showDatePicker && (
          <div className="mt-3 p-3 bg-gray-900 border border-gray-600 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-400">TIME RANGE</span>
              <button
                onClick={() => setShowDatePicker(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: '1 Hour', value: 'now-1h' },
                { label: '24 Hours', value: 'now-24h' },
                { label: '7 Days', value: 'now-7d' },
                { label: '30 Days', value: 'now-30d' }
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    // Update time range filter
                    setShowDatePicker(false);
                  }}
                  className="p-2 text-xs bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded transition-colors"
                >
                  {option.label}
                </button>
              ))}
            </div>
            
            {/* Custom Date Range */}
            <div className="mt-3 pt-3 border-t border-gray-700">
              <span className="text-xs text-gray-400 mb-2 block">Custom Range:</span>
              <div className="flex space-x-2">
                <input
                  type="datetime-local"
                  className="flex-1 px-2 py-1 text-xs bg-gray-800 border border-gray-600 rounded focus:outline-none focus:border-blue-500"
                />
                <span className="text-gray-400 text-xs self-center">to</span>
                <input
                  type="datetime-local"
                  className="flex-1 px-2 py-1 text-xs bg-gray-800 border border-gray-600 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* Query Summary */}
        <div className="mt-2 text-xs text-gray-500">
          <span>
            {filterChips.length === 1 ? 'Showing all events' : `${filterChips.length} filters applied`}
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
      </div>
    </div>
  );
};

export default ContextStrip;
