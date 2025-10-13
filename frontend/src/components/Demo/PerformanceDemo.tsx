/**
 * SYNRGY Performance Demo Component
 * Demonstrates visual rendering optimizations with performance metrics
 */

import { useState, useCallback, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  Zap,
  Gauge,
  TrendingUp,
  Clock,
  Database,
  RefreshCw,
  Settings,
  Info,
} from 'lucide-react'

import EnhancedVisualRenderer from '../Chat/EnhancedVisualRenderer'
import { useVisualPerformance } from '@/hooks/useVisualPerformance'
import type { VisualPayload, VisualCard } from '@/types'

interface PerformanceDemoProps {
  className?: string
}

// Demo data generators
const generateLargeTableData = (rows: number) => ({
  type: 'table' as const,
  title: `Large Table (${rows} rows)`,
  columns: [
    { key: 'timestamp', label: 'Timestamp', type: 'date' },
    { key: 'source', label: 'Source IP', type: 'ip' },
    { key: 'destination', label: 'Destination IP', type: 'ip' },
    { key: 'event', label: 'Event Type', type: 'string' },
    { key: 'severity', label: 'Severity', type: 'number' },
    { key: 'details', label: 'Details', type: 'string' },
  ],
  rows: Array.from({ length: rows }, (_, i) => [
    new Date(Date.now() - Math.random() * 86400000).toISOString(),
    `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    ['login', 'logout', 'file_access', 'network_scan', 'malware'][Math.floor(Math.random() * 5)],
    Math.floor(Math.random() * 10) + 1,
    `Event details ${i} - ${Math.random().toString(36).substring(7)}`,
  ]),
})

const generateLargeChartData = (points: number) => ({
  type: 'chart' as const,
  title: `Time Series Chart (${points} points)`,
  chart_type: 'line' as const,
  data: Array.from({ length: points }, (_, i) => ({
    x: new Date(Date.now() - (points - i) * 60000).toISOString(),
    y: Math.random() * 100 + Math.sin(i / 10) * 20,
    name: `Point ${i}`,
    value: Math.random() * 100,
  })),
  config: {
    x_field: 'x',
    y_field: 'y',
    color: '#00EFFF',
    interactive: true,
  },
})

const generateCompositePayload = (cardCount: number): VisualPayload => ({
  type: 'composite',
  cards: Array.from({ length: cardCount }, (_, i) => {
    const cardType = ['summary_card', 'chart', 'table'][i % 3] as VisualCard['type']
    
    switch (cardType) {
      case 'summary_card':
        return {
          type: 'summary_card',
          title: `Metric ${i + 1}`,
          value: Math.floor(Math.random() * 10000),
          trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as any,
          status: ['success', 'warning', 'error'][Math.floor(Math.random() * 3)] as any,
        }
      case 'chart':
        return generateLargeChartData(Math.floor(Math.random() * 200) + 50)
      case 'table':
        return generateLargeTableData(Math.floor(Math.random() * 500) + 100)
      default:
        return {
          type: 'summary_card',
          title: `Default ${i}`,
          value: 0,
        }
    }
  }),
  metadata: {
    query: `Performance test with ${cardCount} cards`,
    confidence: 0.95,
    execution_time: Math.random() * 1000,
    results_count: cardCount,
  },
})

export default function PerformanceDemo({ className = '' }: PerformanceDemoProps) {
  const [selectedDemo, setSelectedDemo] = useState<string>('composite')
  const [demoSize, setDemoSize] = useState<number>(10)
  const [isGenerating, setIsGenerating] = useState(false)

  // Performance hook for main demo
  const {
    getMetrics,
    resetMetrics,
    clearCache,
  } = useVisualPerformance({
    cacheEnabled: true,
    performanceTracking: true,
    virtualizationThreshold: 20,
  })

  // Demo payload generation
  const demoPayload = useMemo(() => {
    switch (selectedDemo) {
      case 'table':
        return {
          type: 'table',
          ...generateLargeTableData(demoSize * 100),
        } as VisualPayload
      case 'chart':
        return {
          type: 'chart',
          ...generateLargeChartData(demoSize * 50),
        } as VisualPayload
      case 'composite':
        return generateCompositePayload(demoSize)
      default:
        return generateCompositePayload(5)
    }
  }, [selectedDemo, demoSize])

  const handleRegenerateDemo = useCallback(async () => {
    setIsGenerating(true)
    resetMetrics()
    clearCache()
    
    // Simulate generation time
    await new Promise(resolve => setTimeout(resolve, 300))
    setIsGenerating(false)
  }, [resetMetrics, clearCache])

  const performanceMetrics = useMemo(() => getMetrics(), [getMetrics])

  const demoOptions = [
    { value: 'composite', label: 'Composite View', icon: BarChart3 },
    { value: 'table', label: 'Large Table', icon: Database },
    { value: 'chart', label: 'Time Series', icon: TrendingUp },
  ]

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Performance Demo Header */}
      <div className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-synrgy-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-synrgy-text">Visual Performance Demo</h2>
            <p className="text-sm text-synrgy-muted">
              Interactive demonstration of visual rendering optimizations
            </p>
          </div>
        </div>

        {/* Demo Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Demo Type Selection */}
          <div>
            <label className="block text-sm font-medium text-synrgy-text mb-2">
              Demo Type
            </label>
            <div className="space-y-2">
              {demoOptions.map((option) => {
                const Icon = option.icon
                return (
                  <button
                    key={option.value}
                    onClick={() => setSelectedDemo(option.value)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                      selectedDemo === option.value
                        ? 'bg-synrgy-primary/20 border border-synrgy-primary/40 text-synrgy-primary'
                        : 'bg-synrgy-surface/20 border border-synrgy-primary/10 text-synrgy-text hover:bg-synrgy-surface/40'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{option.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Size Control */}
          <div>
            <label className="block text-sm font-medium text-synrgy-text mb-2">
              Data Size ({demoSize})
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={demoSize}
              onChange={(e) => setDemoSize(Number(e.target.value))}
              className="w-full h-2 bg-synrgy-surface/20 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-synrgy-muted mt-1">
              <span>Small</span>
              <span>Large</span>
            </div>
          </div>

          {/* Actions */}
          <div>
            <label className="block text-sm font-medium text-synrgy-text mb-2">
              Actions
            </label>
            <div className="space-y-2">
              <button
                onClick={handleRegenerateDemo}
                disabled={isGenerating}
                className="w-full flex items-center justify-center gap-2 p-3 bg-synrgy-accent/20 hover:bg-synrgy-accent/30 disabled:opacity-50 rounded-lg transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                <span className="text-sm">Regenerate</span>
              </button>
              <button
                onClick={clearCache}
                className="w-full flex items-center justify-center gap-2 p-3 bg-synrgy-muted/20 hover:bg-synrgy-muted/30 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span className="text-sm">Clear Cache</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-synrgy-surface/30 border border-synrgy-primary/20 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Gauge className="w-5 h-5 text-synrgy-primary" />
          <h3 className="text-lg font-semibold text-synrgy-text">Performance Metrics</h3>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-synrgy-surface/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-synrgy-accent" />
              <span className="text-sm text-synrgy-muted">Avg Render Time</span>
            </div>
            <div className="text-2xl font-bold text-synrgy-text">
              {performanceMetrics.averageRenderTime.toFixed(2)}ms
            </div>
          </div>

          <div className="bg-synrgy-surface/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-synrgy-primary" />
              <span className="text-sm text-synrgy-muted">Cache Size</span>
            </div>
            <div className="text-2xl font-bold text-synrgy-text">
              {performanceMetrics.cacheSize}
            </div>
          </div>

          <div className="bg-synrgy-surface/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm text-synrgy-muted">Cache Hit Rate</span>
            </div>
            <div className="text-2xl font-bold text-synrgy-text">
              {((performanceMetrics.cacheHits / (performanceMetrics.cacheHits + performanceMetrics.cacheMisses)) * 100 || 0).toFixed(1)}%
            </div>
          </div>

          <div className="bg-synrgy-surface/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <RefreshCw className="w-4 h-4 text-synrgy-accent" />
              <span className="text-sm text-synrgy-muted">Total Renders</span>
            </div>
            <div className="text-2xl font-bold text-synrgy-text">
              {performanceMetrics.totalRenders}
            </div>
          </div>
        </div>
      </div>

      {/* Demo Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4"
      >
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-400 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-400 mb-1">Optimization Features Active</h4>
            <ul className="text-sm text-blue-300 space-y-1">
              <li>• Payload optimization with data sampling</li>
              <li>• Lazy loading for complex components</li>
              <li>• Virtualization for large datasets (20+ items)</li>
              <li>• Intelligent caching with TTL</li>
              <li>• Performance monitoring and metrics</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Rendered Demo */}
      <div className="bg-synrgy-surface/20 border border-synrgy-primary/10 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-synrgy-text mb-4">Live Demo</h3>
        <EnhancedVisualRenderer
          payload={demoPayload}
          interactive={true}
          onPin={(card) => {
            console.log('Pin action:', card)
          }}
          onExport={(card) => {
            console.log('Export action:', card)
          }}
        />
      </div>
    </div>
  )
}
