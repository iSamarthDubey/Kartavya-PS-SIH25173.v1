/**
 * KARTAVYA SIEM - MiniCharts Component
 * Time series sparklines and bar charts with clickable buckets per blueprint
 */

import React from 'react';
import { TrendingUp, BarChart3, Clock, Activity } from 'lucide-react';

interface DataPoint {
  label: string;
  value: number;
  timestamp?: string;
  color?: string;
}

interface ChartProps {
  data: DataPoint[];
  type: 'sparkline' | 'bar' | 'timeline';
  title?: string;
  height?: number;
  onClick?: (dataPoint: DataPoint) => void;
}

const MiniCharts: React.FC<ChartProps> = ({ 
  data, 
  type, 
  title,
  height = 60,
  onClick 
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-800 rounded p-3 text-center">
        <div className="text-gray-500 text-xs">No data available</div>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));

  const normalizeValue = (value: number) => {
    if (maxValue === minValue) return 0.5;
    return (value - minValue) / (maxValue - minValue);
  };

  const renderSparkline = () => {
    const points = data.map((point, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = (1 - normalizeValue(point.value)) * 100;
      return `${x},${y}`;
    }).join(' ');

    return (
      <div className="bg-gray-800 rounded border border-gray-700 p-3">
        {title && (
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-gray-400">{title}</span>
          </div>
        )}
        
        <div className="relative" style={{ height: `${height}px` }}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            className="overflow-visible"
          >
            {/* Grid lines */}
            <defs>
              <pattern id="grid" width="20" height="25" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 25" fill="none" stroke="#374151" strokeWidth="0.5" opacity="0.3"/>
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid)" />
            
            {/* Area fill */}
            <path
              d={`M 0,100 L ${points} L 100,100 Z`}
              fill="url(#gradient)"
              opacity="0.3"
            />
            
            {/* Line */}
            <polyline
              fill="none"
              stroke="#3B82F6"
              strokeWidth="2"
              points={points}
              className="drop-shadow-sm"
            />
            
            {/* Data points */}
            {data.map((point, index) => {
              const x = (index / (data.length - 1)) * 100;
              const y = (1 - normalizeValue(point.value)) * 100;
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="2"
                  fill="#3B82F6"
                  className={onClick ? "cursor-pointer hover:r-3 transition-all" : ""}
                  onClick={() => onClick?.(point)}
                >
                  <title>{`${point.label}: ${point.value}`}</title>
                </circle>
              );
            })}
            
            {/* Gradient definition */}
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8"/>
                <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.1"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        
        {/* Value display */}
        <div className="flex justify-between items-center mt-2 text-xs">
          <span className="text-gray-400">
            Range: {minValue} - {maxValue}
          </span>
          <span className="text-blue-300 font-mono">
            Latest: {data[data.length - 1]?.value}
          </span>
        </div>
      </div>
    );
  };

  const renderBarChart = () => {
    return (
      <div className="bg-gray-800 rounded border border-gray-700 p-3">
        {title && (
          <div className="flex items-center space-x-2 mb-3">
            <BarChart3 className="w-4 h-4 text-green-400" />
            <span className="text-xs font-semibold text-gray-400">{title}</span>
          </div>
        )}
        
        <div className="flex items-end space-x-1" style={{ height: `${height}px` }}>
          {data.slice(0, 10).map((point, index) => { // Limit to top 10
            const barHeight = (normalizeValue(point.value) * height);
            const color = point.color || '#10B981';
            
            return (
              <div
                key={index}
                className={`flex-1 flex flex-col items-center ${onClick ? 'cursor-pointer' : ''}`}
                onClick={() => onClick?.(point)}
              >
                <div
                  className={`w-full rounded-t transition-all hover:opacity-80 ${
                    onClick ? 'hover:shadow-lg' : ''
                  }`}
                  style={{ 
                    height: `${Math.max(barHeight, 2)}px`, 
                    backgroundColor: color,
                    minHeight: '2px'
                  }}
                  title={`${point.label}: ${point.value}`}
                />
              </div>
            );
          })}
        </div>
        
        {/* Labels */}
        <div className="flex justify-between items-center mt-2 text-xs">
          <div className="flex space-x-1 overflow-hidden">
            {data.slice(0, 3).map((point, index) => (
              <span key={index} className="text-gray-400 truncate">
                {point.label}
              </span>
            ))}
            {data.length > 3 && <span className="text-gray-500">+{data.length - 3}</span>}
          </div>
          <span className="text-green-300 font-mono">
            Max: {maxValue}
          </span>
        </div>
      </div>
    );
  };

  const renderTimeline = () => {
    return (
      <div className="bg-gray-800 rounded border border-gray-700 p-3">
        {title && (
          <div className="flex items-center space-x-2 mb-3">
            <Clock className="w-4 h-4 text-orange-400" />
            <span className="text-xs font-semibold text-gray-400">{title}</span>
          </div>
        )}
        
        <div className="space-y-2">
          {data.slice(0, 5).map((point, index) => { // Show top 5 time periods
            const percentage = (point.value / maxValue) * 100;
            
            return (
              <div
                key={index}
                className={`flex items-center space-x-2 ${onClick ? 'cursor-pointer hover:bg-gray-700 p-1 rounded' : ''}`}
                onClick={() => onClick?.(point)}
              >
                <div className="flex-1 flex items-center space-x-2">
                  <span className="text-xs text-gray-400 w-16 truncate">
                    {point.timestamp ? new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : point.label}
                  </span>
                  
                  <div className="flex-1 bg-gray-700 rounded-full h-2 relative">
                    <div
                      className="bg-orange-400 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  
                  <span className="text-xs text-orange-300 font-mono w-8 text-right">
                    {point.value}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Summary */}
        <div className="mt-3 pt-2 border-t border-gray-700 flex justify-between text-xs">
          <span className="text-gray-400">
            {data.length} time periods
          </span>
          <span className="text-orange-300">
            Total: {data.reduce((sum, d) => sum + d.value, 0)}
          </span>
        </div>
      </div>
    );
  };

  switch (type) {
    case 'sparkline':
      return renderSparkline();
    case 'bar':
      return renderBarChart();
    case 'timeline':
      return renderTimeline();
    default:
      return renderSparkline();
  }
};

// Composite component for multiple charts
export const ChartGrid: React.FC<{ charts: ChartProps[] }> = ({ charts }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {charts.map((chart, index) => (
        <MiniCharts key={index} {...chart} />
      ))}
    </div>
  );
};

// Pre-configured chart components for common SIEM use cases
export const ThreatTimelineChart: React.FC<{ data: DataPoint[]; onClick?: (point: DataPoint) => void }> = ({ data, onClick }) => (
  <MiniCharts 
    data={data} 
    type="sparkline" 
    title="Threat Activity Over Time"
    onClick={onClick}
  />
);

export const TopIPsChart: React.FC<{ data: DataPoint[]; onClick?: (point: DataPoint) => void }> = ({ data, onClick }) => (
  <MiniCharts 
    data={data} 
    type="bar" 
    title="Top Source IPs"
    onClick={onClick}
  />
);

export const HourlyEventsChart: React.FC<{ data: DataPoint[]; onClick?: (point: DataPoint) => void }> = ({ data, onClick }) => (
  <MiniCharts 
    data={data} 
    type="timeline" 
    title="Events by Hour"
    onClick={onClick}
  />
);

export default MiniCharts;
