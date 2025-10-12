/**
 * SYNRGY NarrativeRenderer
 * Rich text and markdown security insights and recommendations
 */

import React from 'react'
import ReactMarkdown from 'react-markdown'
import { FileText, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'
import type { VisualCard } from '@/types'

interface NarrativeRendererProps {
  card: VisualCard
  compact?: boolean
  onError?: (error: any) => void
}

/**
 * Custom markdown components with SYNRGY styling
 */
const markdownComponents = {
  h1: ({ children }: any) => (
    <h1 className="text-xl font-bold text-synrgy-text mb-4 border-b border-synrgy-primary/20 pb-2">
      {children}
    </h1>
  ),
  h2: ({ children }: any) => (
    <h2 className="text-lg font-semibold text-synrgy-text mb-3 mt-6">
      {children}
    </h2>
  ),
  h3: ({ children }: any) => (
    <h3 className="text-base font-medium text-synrgy-text mb-2 mt-4">
      {children}
    </h3>
  ),
  p: ({ children }: any) => (
    <p className="text-synrgy-text mb-3 leading-relaxed">
      {children}
    </p>
  ),
  ul: ({ children }: any) => (
    <ul className="list-disc list-inside mb-3 space-y-1 text-synrgy-text">
      {children}
    </ul>
  ),
  ol: ({ children }: any) => (
    <ol className="list-decimal list-inside mb-3 space-y-1 text-synrgy-text">
      {children}
    </ol>
  ),
  li: ({ children }: any) => (
    <li className="text-synrgy-text ml-2">{children}</li>
  ),
  blockquote: ({ children }: any) => (
    <blockquote className="border-l-4 border-synrgy-primary/50 pl-4 py-2 my-4 bg-synrgy-primary/5 rounded-r">
      <div className="text-synrgy-text italic">{children}</div>
    </blockquote>
  ),
  code: ({ children, inline }: any) => (
    inline ? (
      <code className="bg-synrgy-surface/50 text-synrgy-primary px-1 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    ) : (
      <pre className="bg-synrgy-surface/50 border border-synrgy-primary/20 rounded-lg p-4 overflow-x-auto my-4">
        <code className="text-synrgy-primary text-sm font-mono">{children}</code>
      </pre>
    )
  ),
  strong: ({ children }: any) => (
    <strong className="font-semibold text-synrgy-text">{children}</strong>
  ),
  em: ({ children }: any) => (
    <em className="italic text-synrgy-muted">{children}</em>
  ),
  a: ({ href, children }: any) => (
    <a 
      href={href}
      className="text-synrgy-primary hover:underline"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  )
}

/**
 * Status indicator based on content keywords
 */
const getStatusFromContent = (content: string): {
  status: 'info' | 'success' | 'warning' | 'error'
  icon: React.ComponentType<{ className?: string }>
} => {
  const lowerContent = content.toLowerCase()
  
  if (lowerContent.includes('critical') || lowerContent.includes('threat') || lowerContent.includes('attack')) {
    return { status: 'error', icon: XCircle }
  }
  
  if (lowerContent.includes('warning') || lowerContent.includes('suspicious') || lowerContent.includes('anomaly')) {
    return { status: 'warning', icon: AlertTriangle }
  }
  
  if (lowerContent.includes('secure') || lowerContent.includes('safe') || lowerContent.includes('success')) {
    return { status: 'success', icon: CheckCircle }
  }
  
  return { status: 'info', icon: Info }
}

/**
 * Status color mapping
 */
const STATUS_COLORS = {
  info: 'border-synrgy-primary/20 bg-synrgy-primary/5',
  success: 'border-green-500/20 bg-green-500/5',
  warning: 'border-yellow-500/20 bg-yellow-500/5',
  error: 'border-red-500/20 bg-red-500/5'
}

const STATUS_ICON_COLORS = {
  info: 'text-synrgy-primary',
  success: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500'
}

const NarrativeRenderer: React.FC<NarrativeRendererProps> = ({
  card,
  compact = false,
  onError
}) => {
  try {
    const content = card.data || card.title || ''
    
    if (!content) {
      return (
        <div className="p-6 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10 text-center">
          <FileText className="w-8 h-8 text-synrgy-muted mx-auto mb-2" />
          <p className="text-synrgy-muted text-sm">No narrative content available</p>
        </div>
      )
    }
    
    // Detect status from content
    const { status, icon: StatusIcon } = getStatusFromContent(content)
    const statusColor = STATUS_COLORS[status]
    const iconColor = STATUS_ICON_COLORS[status]
    
    return (
      <div className={`
        bg-synrgy-surface/50 rounded-lg border p-4
        ${statusColor}
        ${compact ? 'p-3' : 'p-4'}
      `}>
        {/* Header */}
        {card.title && (
          <div className="flex items-center gap-2 mb-4">
            <StatusIcon className={`w-5 h-5 ${iconColor}`} />
            <h3 className={`font-medium text-synrgy-text ${compact ? 'text-sm' : 'text-base'}`}>
              {card.title}
            </h3>
          </div>
        )}
        
        {/* Content */}
        <div className={`prose prose-sm max-w-none ${compact ? 'text-sm' : ''}`}>
          <ReactMarkdown components={markdownComponents}>
            {String(content)}
          </ReactMarkdown>
        </div>
        
        {/* Subtitle */}
        {card.subtitle && !compact && (
          <div className="mt-4 pt-3 border-t border-synrgy-primary/10">
            <p className="text-xs text-synrgy-muted italic">
              {card.subtitle}
            </p>
          </div>
        )}
        
        {/* Metadata */}
        {card.metadata && !compact && process.env.NODE_ENV === 'development' && (
          <details className="mt-4 pt-3 border-t border-synrgy-primary/10">
            <summary className="text-xs text-synrgy-muted cursor-pointer hover:text-synrgy-text">
              Metadata
            </summary>
            <pre className="mt-2 p-2 bg-synrgy-surface/50 rounded text-xs text-synrgy-muted overflow-auto">
              {JSON.stringify(card.metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>
    )
  } catch (error) {
    onError?.(error)
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-red-400 text-sm">
          Failed to render narrative: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }
}

export default NarrativeRenderer
