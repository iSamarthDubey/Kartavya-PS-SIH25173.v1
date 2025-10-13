/**
 * SYNRGY Visual Performance Optimization Hook
 * Provides caching, virtualization decisions, and performance measurements
 * for the enhanced visual rendering system
 */

import { useRef, useEffect, useCallback, useMemo } from 'react'
import type { VisualPayload, VisualCard } from '@/types'

interface PerformanceMetrics {
  renderTime: number
  cacheHits: number
  cacheMisses: number
  totalRenders: number
  averageRenderTime: number
  lastRenderTime: number
}

interface VirtualizationConfig {
  enabled: boolean
  threshold: number
  chunkSize: number
  overscan: number
}

interface CacheEntry {
  data: any
  timestamp: number
  accessCount: number
  size: number
}

interface UseVisualPerformanceOptions {
  cacheEnabled?: boolean
  cacheTtl?: number // Time to live in milliseconds
  maxCacheSize?: number // Maximum cache entries
  virtualizationThreshold?: number // Minimum items to enable virtualization
  performanceTracking?: boolean
}

const DEFAULT_OPTIONS: Required<UseVisualPerformanceOptions> = {
  cacheEnabled: true,
  cacheTtl: 5 * 60 * 1000, // 5 minutes
  maxCacheSize: 100,
  virtualizationThreshold: 50,
  performanceTracking: true,
}

/**
 * Hook for optimizing visual rendering performance
 */
export function useVisualPerformance(options: UseVisualPerformanceOptions = {}) {
  const config = useMemo(() => ({ ...DEFAULT_OPTIONS, ...options }), [options])
  
  // Performance metrics
  const metricsRef = useRef<PerformanceMetrics>({
    renderTime: 0,
    cacheHits: 0,
    cacheMisses: 0,
    totalRenders: 0,
    averageRenderTime: 0,
    lastRenderTime: 0,
  })

  // Cache storage
  const cacheRef = useRef<Map<string, CacheEntry>>(new Map())
  
  // Performance tracking
  const startTimeRef = useRef<number>(0)

  /**
   * Generate cache key for visual payload
   */
  const getCacheKey = useCallback((payload: VisualPayload): string => {
    const key = JSON.stringify({
      type: payload.type,
      cards: payload.cards?.map(card => ({
        type: card.type,
        title: card.title,
        dataHash: typeof card.data === 'object' ? JSON.stringify(card.data).slice(0, 100) : card.data,
      })),
      metadata: payload.metadata ? {
        query: payload.metadata.query,
        results_count: payload.metadata.results_count,
      } : null,
    })
    
    // Create hash from key for shorter cache keys
    let hash = 0
    for (let i = 0; i < key.length; i++) {
      const char = key.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return `visual_${Math.abs(hash)}`
  }, [])

  /**
   * Check if payload should use virtualization
   */
  const shouldVirtualize = useCallback((payload: VisualPayload): VirtualizationConfig => {
    if (!payload.cards || payload.cards.length < config.virtualizationThreshold) {
      return {
        enabled: false,
        threshold: config.virtualizationThreshold,
        chunkSize: 10,
        overscan: 3,
      }
    }

    // Check for large tables or datasets
    const hasLargeData = payload.cards.some(card => {
      if (card.type === 'table' && card.rows) {
        return card.rows.length > 100
      }
      if (card.type === 'chart' && Array.isArray(card.data)) {
        return card.data.length > 200
      }
      return false
    })

    return {
      enabled: true,
      threshold: config.virtualizationThreshold,
      chunkSize: hasLargeData ? 20 : 10,
      overscan: hasLargeData ? 5 : 3,
    }
  }, [config.virtualizationThreshold])

  /**
   * Clean expired cache entries
   */
  const cleanCache = useCallback(() => {
    if (!config.cacheEnabled) return

    const now = Date.now()
    const cache = cacheRef.current
    const expiredKeys: string[] = []

    cache.forEach((entry, key) => {
      if (now - entry.timestamp > config.cacheTtl) {
        expiredKeys.push(key)
      }
    })

    expiredKeys.forEach(key => cache.delete(key))

    // If cache is still too large, remove least recently used items
    if (cache.size > config.maxCacheSize) {
      const entries = Array.from(cache.entries())
      entries.sort(([, a], [, b]) => a.accessCount - b.accessCount)
      
      const toRemove = cache.size - config.maxCacheSize + 10 // Remove extra 10 for buffer
      for (let i = 0; i < toRemove && i < entries.length; i++) {
        cache.delete(entries[i][0])
      }
    }
  }, [config.cacheEnabled, config.cacheTtl, config.maxCacheSize])

  /**
   * Get cached data for payload
   */
  const getCachedData = useCallback((payload: VisualPayload) => {
    if (!config.cacheEnabled) return null

    const key = getCacheKey(payload)
    const entry = cacheRef.current.get(key)

    if (!entry) {
      metricsRef.current.cacheMisses++
      return null
    }

    const now = Date.now()
    if (now - entry.timestamp > config.cacheTtl) {
      cacheRef.current.delete(key)
      metricsRef.current.cacheMisses++
      return null
    }

    entry.accessCount++
    metricsRef.current.cacheHits++
    return entry.data
  }, [config.cacheEnabled, getCacheKey, config.cacheTtl])

  /**
   * Cache processed data
   */
  const setCachedData = useCallback((payload: VisualPayload, data: any) => {
    if (!config.cacheEnabled) return

    const key = getCacheKey(payload)
    const entry: CacheEntry = {
      data,
      timestamp: Date.now(),
      accessCount: 1,
      size: JSON.stringify(data).length,
    }

    cacheRef.current.set(key, entry)
    
    // Clean cache periodically
    if (cacheRef.current.size > config.maxCacheSize * 1.2) {
      cleanCache()
    }
  }, [config.cacheEnabled, getCacheKey, config.maxCacheSize, cleanCache])

  /**
   * Start performance measurement
   */
  const startRenderMeasurement = useCallback(() => {
    if (!config.performanceTracking) return

    startTimeRef.current = performance.now()
  }, [config.performanceTracking])

  /**
   * End performance measurement
   */
  const endRenderMeasurement = useCallback(() => {
    if (!config.performanceTracking || !startTimeRef.current) return

    const endTime = performance.now()
    const renderTime = endTime - startTimeRef.current
    const metrics = metricsRef.current

    metrics.renderTime += renderTime
    metrics.totalRenders++
    metrics.lastRenderTime = renderTime
    metrics.averageRenderTime = metrics.renderTime / metrics.totalRenders

    startTimeRef.current = 0
  }, [config.performanceTracking])

  /**
   * Get current performance metrics
   */
  const getMetrics = useCallback((): PerformanceMetrics & { cacheSize: number } => {
    return {
      ...metricsRef.current,
      cacheSize: cacheRef.current.size,
    }
  }, [])

  /**
   * Reset performance metrics
   */
  const resetMetrics = useCallback(() => {
    metricsRef.current = {
      renderTime: 0,
      cacheHits: 0,
      cacheMisses: 0,
      totalRenders: 0,
      averageRenderTime: 0,
      lastRenderTime: 0,
    }
  }, [])

  /**
   * Clear cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current.clear()
  }, [])

  /**
   * Optimize payload for rendering
   */
  const optimizePayload = useCallback((payload: VisualPayload): VisualPayload => {
    // Check cache first
    const cached = getCachedData(payload)
    if (cached) {
      return cached
    }

    startRenderMeasurement()

    try {
      // Create optimized payload
      const optimized: VisualPayload = {
        ...payload,
        cards: payload.cards?.map(card => {
          // Optimize table data
          if (card.type === 'table' && card.rows && card.rows.length > 1000) {
            return {
              ...card,
              rows: card.rows.slice(0, 1000), // Limit to first 1000 rows
              pagination: {
                total: card.rows.length,
                page: 1,
                per_page: 1000,
              },
            }
          }

          // Optimize chart data
          if (card.type === 'chart' && Array.isArray(card.data) && card.data.length > 500) {
            // Sample data for better performance
            const step = Math.ceil(card.data.length / 500)
            return {
              ...card,
              data: card.data.filter((_, index) => index % step === 0),
            }
          }

          return card
        }),
      }

      // Cache the optimized payload
      setCachedData(payload, optimized)

      return optimized
    } finally {
      endRenderMeasurement()
    }
  }, [getCachedData, setCachedData, startRenderMeasurement, endRenderMeasurement])

  /**
   * Determine if component should use lazy loading
   */
  const shouldLazyLoad = useCallback((card: VisualCard): boolean => {
    // Lazy load large tables
    if (card.type === 'table' && card.rows && card.rows.length > 100) {
      return true
    }

    // Lazy load complex charts
    if (card.type === 'chart' && Array.isArray(card.data) && card.data.length > 200) {
      return true
    }

    // Lazy load network graphs (always complex)
    if (card.type === 'network_graph') {
      return true
    }

    return false
  }, [])

  // Clean cache on unmount
  useEffect(() => {
    const interval = setInterval(cleanCache, 60000) // Clean every minute
    return () => {
      clearInterval(interval)
    }
  }, [cleanCache])

  return {
    // Core functions
    optimizePayload,
    shouldVirtualize,
    shouldLazyLoad,
    
    // Cache management
    getCachedData,
    setCachedData,
    clearCache,
    
    // Performance tracking
    startRenderMeasurement,
    endRenderMeasurement,
    getMetrics,
    resetMetrics,
    
    // Configuration
    config,
  }
}

/**
 * Hook for measuring component render performance
 */
export function useRenderPerformance(componentName: string) {
  const renderCountRef = useRef(0)
  const lastRenderTimeRef = useRef(0)

  useEffect(() => {
    renderCountRef.current++
    lastRenderTimeRef.current = performance.now()
  })

  const getStats = useCallback(() => {
    return {
      componentName,
      renderCount: renderCountRef.current,
      lastRenderTime: lastRenderTimeRef.current,
    }
  }, [componentName])

  return { getStats }
}

export default useVisualPerformance
