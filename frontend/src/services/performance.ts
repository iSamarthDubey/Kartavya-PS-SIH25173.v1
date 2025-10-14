/**
 * SYNRGY Performance Monitoring & Analytics Service
 * Real-time performance tracking, user analytics, and system monitoring
 */

import React from 'react'

interface PerformanceMetric {
  id: string
  name: string
  value: number
  timestamp: number
  category: 'navigation' | 'rendering' | 'network' | 'custom'
  metadata?: Record<string, any>
}

interface UserEvent {
  id: string
  type: 'page_view' | 'click' | 'search' | 'error' | 'api_call' | 'custom'
  target?: string
  value?: any
  timestamp: number
  session_id: string
  user_id?: string
  metadata?: Record<string, any>
}

interface PerformanceSnapshot {
  timestamp: number
  metrics: {
    // Core Web Vitals
    lcp?: number // Largest Contentful Paint
    fid?: number // First Input Delay
    cls?: number // Cumulative Layout Shift
    fcp?: number // First Contentful Paint
    ttfb?: number // Time to First Byte
    
    // Memory
    memory_used?: number
    memory_limit?: number
    
    // Network
    connection_type?: string
    connection_speed?: string
    
    // Bundle
    bundle_size?: number
    chunks_loaded?: number
  }
  system: {
    user_agent: string
    viewport: { width: number; height: number }
    device_type: 'mobile' | 'tablet' | 'desktop'
    os: string
    browser: string
  }
}

class PerformanceMonitoringService {
  private static instance: PerformanceMonitoringService
  private metrics: PerformanceMetric[] = []
  private events: UserEvent[] = []
  private sessionId: string
  private userId?: string
  private observers: PerformanceObserver[] = []
  private analyticsEnabled: boolean
  private reportingEnabled: boolean
  private maxMetrics = 1000
  private maxEvents = 500
  private reportingInterval = 30000 // 30 seconds

  constructor() {
    this.sessionId = this.generateSessionId()
    this.analyticsEnabled = import.meta.env.VITE_ENABLE_ANALYTICS === 'true'
    this.reportingEnabled = import.meta.env.VITE_ENABLE_PERFORMANCE_REPORTING === 'true'
    
    this.initializeMonitoring()
    this.startPeriodicReporting()
  }

  static getInstance(): PerformanceMonitoringService {
    if (!PerformanceMonitoringService.instance) {
      PerformanceMonitoringService.instance = new PerformanceMonitoringService()
    }
    return PerformanceMonitoringService.instance
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private initializeMonitoring() {
    if (!this.analyticsEnabled) return

    // Monitor navigation timing
    this.observeNavigationTiming()
    
    // Monitor resource loading
    this.observeResourceTiming()
    
    // Monitor layout shifts and paint timing
    this.observeLayoutShifts()
    this.observePaintTiming()
    
    // Monitor long tasks
    this.observeLongTasks()
    
    // Monitor memory usage
    this.observeMemoryUsage()
    
    // Set up page visibility change tracking
    this.setupVisibilityTracking()
    
    // Track initial page load
    this.trackPageView(window.location.pathname)
  }

  private observeNavigationTiming() {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const navigationEntries = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[]
      
      navigationEntries.forEach(entry => {
        this.recordMetric('navigation', 'dns_lookup', entry.domainLookupEnd - entry.domainLookupStart)
        this.recordMetric('navigation', 'tcp_connect', entry.connectEnd - entry.connectStart)
        this.recordMetric('navigation', 'ttfb', entry.responseStart - entry.requestStart)
        this.recordMetric('navigation', 'dom_content_loaded', entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart)
        this.recordMetric('navigation', 'load_complete', entry.loadEventEnd - entry.loadEventStart)
      })
    }
  }

  private observeResourceTiming() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(entry => {
          if (entry.entryType === 'resource') {
            const resourceEntry = entry as PerformanceResourceTiming
            
            // Track slow resources
            if (resourceEntry.duration > 1000) {
              this.recordMetric('network', 'slow_resource', resourceEntry.duration, {
                name: resourceEntry.name,
                type: resourceEntry.initiatorType,
                size: resourceEntry.transferSize,
              })
            }
            
            // Track failed resources
            if (resourceEntry.transferSize === 0 && resourceEntry.duration > 0) {
              this.recordEvent('error', 'resource_load_failed', resourceEntry.name)
            }
          }
        })
      })
      
      observer.observe({ entryTypes: ['resource'] })
      this.observers.push(observer)
    }
  }

  private observeLayoutShifts() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        let clsValue = 0
        list.getEntries().forEach(entry => {
          if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
          }
        })
        
        if (clsValue > 0) {
          this.recordMetric('rendering', 'cls', clsValue)
        }
      })
      
      observer.observe({ entryTypes: ['layout-shift'] })
      this.observers.push(observer)
    }
  }

  private observePaintTiming() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(entry => {
          if (entry.name === 'first-contentful-paint') {
            this.recordMetric('rendering', 'fcp', entry.startTime)
          } else if (entry.name === 'largest-contentful-paint') {
            this.recordMetric('rendering', 'lcp', entry.startTime)
          }
        })
      })
      
      observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] })
      this.observers.push(observer)
    }
  }

  private observeLongTasks() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(entry => {
          this.recordMetric('rendering', 'long_task', entry.duration, {
            start_time: entry.startTime,
            name: entry.name,
          })
        })
      })
      
      observer.observe({ entryTypes: ['longtask'] })
      this.observers.push(observer)
    }
  }

  private observeMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      
      setInterval(() => {
        this.recordMetric('custom', 'memory_used', memory.usedJSHeapSize)
        this.recordMetric('custom', 'memory_total', memory.totalJSHeapSize)
        this.recordMetric('custom', 'memory_limit', memory.jsHeapSizeLimit)
      }, 10000) // Every 10 seconds
    }
  }

  private setupVisibilityTracking() {
    let startTime = Date.now()
    
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        const timeSpent = Date.now() - startTime
        this.recordMetric('custom', 'time_on_page', timeSpent)
      } else {
        startTime = Date.now()
      }
    })
  }

  private recordMetric(
    category: PerformanceMetric['category'],
    name: string,
    value: number,
    metadata?: Record<string, any>
  ) {
    const metric: PerformanceMetric = {
      id: `metric_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      value,
      timestamp: Date.now(),
      category,
      metadata,
    }

    this.metrics.push(metric)
    
    // Keep metrics array under limit
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics)
    }
    
    // Log to console in debug mode
    if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
      console.log(`📊 Performance Metric: ${category}/${name} = ${value}`, metadata)
    }
  }

  private recordEvent(
    type: UserEvent['type'],
    target?: string,
    value?: any,
    metadata?: Record<string, any>
  ) {
    if (!this.analyticsEnabled) return

    const event: UserEvent = {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      target,
      value,
      timestamp: Date.now(),
      session_id: this.sessionId,
      user_id: this.userId,
      metadata,
    }

    this.events.push(event)
    
    // Keep events array under limit
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents)
    }
    
    // Log to console in debug mode
    if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
      console.log(`📈 User Event: ${type}`, { target, value, metadata })
    }
  }

  // Public API methods

  public setUserId(userId: string) {
    this.userId = userId
    sessionStorage.setItem('synrgy_user_id', userId)
  }

  public trackPageView(path: string) {
    this.recordEvent('page_view', path, null, {
      referrer: document.referrer,
      timestamp: Date.now(),
    })
  }

  public trackClick(target: string, metadata?: Record<string, any>) {
    this.recordEvent('click', target, null, metadata)
  }

  public trackSearch(query: string, results?: number) {
    this.recordEvent('search', query, results, {
      query_length: query.length,
      has_results: results !== undefined && results > 0,
    })
  }

  public trackApiCall(endpoint: string, method: string, duration: number, status: number) {
    this.recordMetric('network', 'api_call', duration, {
      endpoint,
      method,
      status,
      success: status >= 200 && status < 300,
    })
    
    this.recordEvent('api_call', endpoint, { method, duration, status })
  }

  public trackCustomMetric(name: string, value: number, metadata?: Record<string, any>) {
    this.recordMetric('custom', name, value, metadata)
  }

  public trackCustomEvent(type: string, target?: string, value?: any, metadata?: Record<string, any>) {
    this.recordEvent('custom' as any, target, value, { type, ...metadata })
  }

  public getMetrics(category?: PerformanceMetric['category']): PerformanceMetric[] {
    return category 
      ? this.metrics.filter(m => m.category === category)
      : [...this.metrics]
  }

  public getEvents(type?: UserEvent['type']): UserEvent[] {
    return type
      ? this.events.filter(e => e.type === type)
      : [...this.events]
  }

  public getPerformanceSnapshot(): PerformanceSnapshot {
    const now = Date.now()
    const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    return {
      timestamp: now,
      metrics: {
        lcp: this.getLatestMetric('rendering', 'lcp'),
        fcp: this.getLatestMetric('rendering', 'fcp'),
        cls: this.getLatestMetric('rendering', 'cls'),
        ttfb: navigationEntry ? navigationEntry.responseStart - navigationEntry.requestStart : undefined,
        memory_used: this.getLatestMetric('custom', 'memory_used'),
        memory_limit: this.getLatestMetric('custom', 'memory_limit'),
      },
      system: {
        user_agent: navigator.userAgent,
        viewport: { width: window.innerWidth, height: window.innerHeight },
        device_type: this.detectDeviceType(),
        os: this.detectOS(),
        browser: this.detectBrowser(),
      },
    }
  }

  private getLatestMetric(category: string, name: string): number | undefined {
    const metric = this.metrics
      .filter(m => m.category === category && m.name === name)
      .sort((a, b) => b.timestamp - a.timestamp)[0]
    
    return metric?.value
  }

  private detectDeviceType(): 'mobile' | 'tablet' | 'desktop' {
    const width = window.innerWidth
    if (width <= 768) return 'mobile'
    if (width <= 1024) return 'tablet'
    return 'desktop'
  }

  private detectOS(): string {
    const userAgent = navigator.userAgent
    if (userAgent.includes('Windows')) return 'Windows'
    if (userAgent.includes('Mac OS')) return 'macOS'
    if (userAgent.includes('Linux')) return 'Linux'
    if (userAgent.includes('Android')) return 'Android'
    if (userAgent.includes('iOS')) return 'iOS'
    return 'Unknown'
  }

  private detectBrowser(): string {
    const userAgent = navigator.userAgent
    if (userAgent.includes('Chrome')) return 'Chrome'
    if (userAgent.includes('Firefox')) return 'Firefox'
    if (userAgent.includes('Safari')) return 'Safari'
    if (userAgent.includes('Edge')) return 'Edge'
    return 'Unknown'
  }

  private startPeriodicReporting() {
    if (!this.reportingEnabled) return

    setInterval(() => {
      this.reportToBackend()
    }, this.reportingInterval)
  }

  private async reportToBackend() {
    if (!this.reportingEnabled || (this.metrics.length === 0 && this.events.length === 0)) {
      return
    }

    try {
      const payload = {
        session_id: this.sessionId,
        user_id: this.userId,
        timestamp: Date.now(),
        metrics: [...this.metrics],
        events: [...this.events],
        snapshot: this.getPerformanceSnapshot(),
      }

      const response = await fetch('/api/analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        // Clear reported data
        this.metrics = []
        this.events = []
        
        if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
          console.log('📊 Performance data reported to backend')
        }
      }
    } catch (error) {
      if (import.meta.env.VITE_ENABLE_DEBUG === 'true') {
        console.warn('Failed to report performance data:', error)
      }
    }
  }

  public destroy() {
    // Clean up observers
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
    
    // Clear data
    this.metrics = []
    this.events = []
  }
}

export const performanceMonitor = PerformanceMonitoringService.getInstance()

// React hook for performance monitoring
export function usePerformanceMonitoring() {
  const [metrics, setMetrics] = React.useState<PerformanceMetric[]>([])
  
  React.useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(performanceMonitor.getMetrics())
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])
  
  return {
    metrics,
    trackClick: performanceMonitor.trackClick.bind(performanceMonitor),
    trackSearch: performanceMonitor.trackSearch.bind(performanceMonitor),
    trackCustomMetric: performanceMonitor.trackCustomMetric.bind(performanceMonitor),
    trackCustomEvent: performanceMonitor.trackCustomEvent.bind(performanceMonitor),
    getSnapshot: () => performanceMonitor.getPerformanceSnapshot(),
  }
}

export default PerformanceMonitoringService
