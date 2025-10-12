/**
 * SYNRGY VisualRenderer - Heart of the Visual System
 * Handles all visual_payload types from backend
 * Based on SYNRGY.TXT lines 592-600
 */

import React, { Suspense, useState, useCallback } from 'react'
import { AlertCircle, Loader2, Pin, Download, ExternalLink } from 'lucide-react'
import type { VisualRendererProps, VisualCard, VisualError, PinToDashboardConfig, ExportConfig } from '@/types'

// Lazy load renderers for better performance
const SummaryCardRenderer = React.lazy(() => import('./SummaryCardRenderer'))
const ChartRenderer = React.lazy(() => import('./ChartRenderer'))
const TableRenderer = React.lazy(() => import('./TableRenderer'))
const MapRenderer = React.lazy(() => import('./MapRenderer'))
const NetworkRenderer = React.lazy(() => import('./NetworkRenderer'))
const NarrativeRenderer = React.lazy(() => import('./NarrativeRenderer'))

/**
 * Loading fallback for lazy-loaded renderers
 */
const RendererFallback: React.FC<{ type: string }> = ({ type }) => (
  <div className="flex items-center justify-center p-6 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/20">
    <Loader2 className="w-5 h-5 animate-spin text-synrgy-primary mr-3" />
    <span className="text-synrgy-muted text-sm">Loading {type} renderer...</span>
  </div>
)

/**
 * Error boundary for individual renderers
 */
const RendererErrorFallback: React.FC<{ 
  error: string
  retry?: () => void
  type: string 
}> = ({ error, retry, type }) => (
  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
    <div className="flex items-center gap-2 text-red-400 mb-2">
      <AlertCircle className="w-4 h-4" />
      <span className="font-medium">Rendering Error</span>
    </div>
    <p className="text-sm text-synrgy-muted mb-3">
      Failed to render {type}: {error}
    </p>
    {retry && (
      <button 
        onClick={retry}
        className="text-xs px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded border border-red-500/30 text-red-300"
      >
        Retry
      </button>
    )}
  </div>
)

/**
 * Action buttons for visual cards
 */
const CardActions: React.FC<{
  card: VisualCard
  onPin?: (config: PinToDashboardConfig) => void
  onExport?: (config: ExportConfig) => void
  onAction?: (action: string, context: any) => void
}> = ({ card, onPin, onExport, onAction }) => {
  const canPin = card.config?.pinnable !== false && onPin
  const canExport = card.config?.exportable !== false && onExport
  
  const handlePin = useCallback(() => {
    if (!onPin) return
    
    const config: PinToDashboardConfig = {
      widgetType: card.type,
      title: card.title || `${card.type} Widget`,
      data: card.data,
      filters: {}
    }
    
    onPin(config)
  }, [card, onPin])
  
  const handleExport = useCallback(() => {
    if (!onExport) return
    
    const config: ExportConfig = {
      format: 'png',
      filename: `${card.title || card.type}_${Date.now()}`
    }
    
    onExport(config)
  }, [card, onExport])

  if (!canPin && !canExport && !card.actions?.length) {
    return null
  }

  return (
    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2 flex gap-1">
      {canPin && (
        <button
          onClick={handlePin}
          className="p-1.5 bg-synrgy-surface/90 hover:bg-synrgy-primary/20 rounded border border-synrgy-primary/20 text-synrgy-primary"
          title="Pin to Dashboard"
        >
          <Pin className="w-3 h-3" />
        </button>
      )}
      
      {canExport && (
        <button
          onClick={handleExport}
          className="p-1.5 bg-synrgy-surface/90 hover:bg-synrgy-accent/20 rounded border border-synrgy-accent/20 text-synrgy-accent"
          title="Export"
        >
          <Download className="w-3 h-3" />
        </button>
      )}
      
      {card.actions?.map((action, idx) => (
        <button
          key={idx}
          onClick={() => onAction?.(action.type, action.context)}
          className="p-1.5 bg-synrgy-surface/90 hover:bg-synrgy-muted/20 rounded border border-synrgy-muted/20 text-synrgy-muted"
          title={action.label}
        >
          <ExternalLink className="w-3 h-3" />
        </button>
      ))}
    </div>
  )
}

/**
 * Individual card renderer with error boundary
 */
const CardRenderer: React.FC<{
  card: VisualCard
  onPin?: (config: PinToDashboardConfig) => void
  onExport?: (config: ExportConfig) => void
  onAction?: (action: string, context: any) => void
  onError?: (error: VisualError) => void
  compact?: boolean
}> = ({ card, onPin, onExport, onAction, onError, compact }) => {
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const handleError = useCallback((err: any) => {
    const errorMsg = err?.message || 'Unknown rendering error'
    setError(errorMsg)
    
    onError?.({
      type: 'render_error',
      message: errorMsg,
      details: err,
      recoverable: true
    })
  }, [onError])

  const retry = useCallback(() => {
    setError(null)
    setRetryCount(prev => prev + 1)
  }, [])

  if (error) {
    return <RendererErrorFallback error={error} retry={retry} type={card.type} />
  }

  const commonProps = {
    card,
    compact,
    onError: handleError
  }

  return (
    <div className="relative group">
      <Suspense fallback={<RendererFallback type={card.type} />}>
        {card.type === 'summary_card' && <SummaryCardRenderer {...commonProps} />}
        {card.type === 'chart' && <ChartRenderer {...commonProps} />}
        {card.type === 'table' && <TableRenderer {...commonProps} />}
        {card.type === 'map' && <MapRenderer {...commonProps} />}
        {card.type === 'network_graph' && <NetworkRenderer {...commonProps} />}
        {card.type === 'narrative' && <NarrativeRenderer {...commonProps} />}
      </Suspense>
      
      <CardActions 
        card={card}
        onPin={onPin}
        onExport={onExport}
        onAction={onAction}
      />
    </div>
  )
}

/**
 * Main VisualRenderer component
 */
const VisualRenderer: React.FC<VisualRendererProps> = ({
  payload,
  className = '',
  onPin,
  onExport,
  onAction,
  onError,
  interactive = true,
  compact = false
}) => {
  const [globalError, setGlobalError] = useState<string | null>(null)

  const handleGlobalError = useCallback((error: VisualError) => {
    setGlobalError(error.message)
    onError?.(error)
  }, [onError])

  // Handle composite payload with multiple cards
  if (payload.type === 'composite' && payload.cards) {
    return (
      <div className={`synrgy-visual-renderer ${className}`}>
        {globalError && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {globalError}
          </div>
        )}
        
        <div className="space-y-4">
          {payload.cards.map((card, index) => (
            <CardRenderer
              key={`card-${index}`}
              card={card}
              onPin={onPin}
              onExport={onExport}
              onAction={onAction}
              onError={handleGlobalError}
              compact={compact}
            />
          ))}
        </div>
        
        {/* Metadata display for debugging */}
        {payload.metadata && process.env.NODE_ENV === 'development' && (
          <details className="mt-4 text-xs">
            <summary className="text-synrgy-muted cursor-pointer">Debug Info</summary>
            <pre className="mt-2 p-2 bg-synrgy-surface/50 rounded text-synrgy-muted overflow-auto">
              {JSON.stringify(payload.metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>
    )
  }

  // Handle single card payload
  const singleCard: VisualCard = {
    type: payload.type as any,
    data: payload.cards?.[0]?.data || [],
    ...payload.cards?.[0]
  }

  return (
    <div className={`synrgy-visual-renderer ${className}`}>
      {globalError && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {globalError}
        </div>
      )}
      
      <CardRenderer
        card={singleCard}
        onPin={onPin}
        onExport={onExport}
        onAction={onAction}
        onError={handleGlobalError}
        compact={compact}
      />
    </div>
  )
}

export default VisualRenderer
