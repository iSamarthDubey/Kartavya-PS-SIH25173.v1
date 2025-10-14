/**
 * SYNRGY Gauge Chart Component
 * Displays circular gauge meters for system health and performance metrics
 */

import { useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface GaugeChartProps {
  value: number // 0-100
  max?: number
  title: string
  unit?: string
  color?: string
  backgroundColor?: string
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  critical?: number
  warning?: number
}

const GAUGE_COLORS = {
  excellent: '#22C55E',   // green-500
  good: '#00EFFF',        // synrgy-primary  
  warning: '#F59E0B',     // amber-500
  critical: '#EF4444',    // red-500
  background: '#1E293B'   // slate-800
}

export default function GaugeChart({
  value,
  max = 100,
  title,
  unit = '%',
  color,
  backgroundColor = GAUGE_COLORS.background,
  size = 'md',
  showValue = true,
  critical = 80,
  warning = 60
}: GaugeChartProps) {
  
  const percentage = Math.min(Math.max(value / max * 100, 0), 100)
  
  // Determine color based on value thresholds
  const getGaugeColor = useMemo(() => {
    if (color) return color
    
    if (percentage >= critical) return GAUGE_COLORS.critical
    if (percentage >= warning) return GAUGE_COLORS.warning  
    if (percentage >= 40) return GAUGE_COLORS.good
    return GAUGE_COLORS.excellent
  }, [percentage, critical, warning, color])
  
  // Create gauge data (semicircle)
  const gaugeData = useMemo(() => [
    { name: 'value', value: percentage, fill: getGaugeColor },
    { name: 'empty', value: 100 - percentage, fill: backgroundColor }
  ], [percentage, getGaugeColor, backgroundColor])
  
  const sizes = {
    sm: { width: 120, height: 80, innerRadius: 35, outerRadius: 55, fontSize: 'text-sm' },
    md: { width: 160, height: 100, innerRadius: 45, outerRadius: 70, fontSize: 'text-base' },
    lg: { width: 200, height: 120, innerRadius: 60, outerRadius: 90, fontSize: 'text-lg' }
  }
  
  const sizeConfig = sizes[size]
  
  return (
    <div className="flex flex-col items-center">
      <div 
        className="relative"
        style={{ width: sizeConfig.width, height: sizeConfig.height }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={gaugeData}
              cx="50%"
              cy="85%"
              startAngle={180}
              endAngle={0}
              innerRadius={sizeConfig.innerRadius}
              outerRadius={sizeConfig.outerRadius}
              paddingAngle={0}
              dataKey="value"
            >
              {gaugeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Value display in center */}
        {showValue && (
          <div 
            className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-center"
            style={{ color: getGaugeColor }}
          >
            <div className={`font-bold ${sizeConfig.fontSize}`}>
              {value.toLocaleString()}{unit}
            </div>
            <div className="text-xs text-synrgy-muted opacity-75">
              of {max.toLocaleString()}{unit}
            </div>
          </div>
        )}
      </div>
      
      {/* Title */}
      <div className="mt-2 text-center">
        <div className="text-sm font-medium text-synrgy-text">{title}</div>
      </div>
    </div>
  )
}
