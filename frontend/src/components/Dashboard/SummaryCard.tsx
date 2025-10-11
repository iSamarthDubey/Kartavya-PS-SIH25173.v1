import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  MessageSquare,
  MoreVertical
} from 'lucide-react'

import type { SummaryCard } from '@/types'

interface SummaryCardProps {
  card: SummaryCard
  index?: number
  onAskSynrgy?: (context: string) => void
  className?: string
}

export default function SummaryCardComponent({ 
  card, 
  index = 0, 
  onAskSynrgy, 
  className = '' 
}: SummaryCardProps) {
  
  const getTrendIcon = () => {
    if (!card.change) return <Minus className="w-4 h-4" />
    
    switch (card.change.trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />
      case 'down':
        return <TrendingDown className="w-4 h-4" />
      default:
        return <Minus className="w-4 h-4" />
    }
  }

  const getTrendColor = () => {
    if (!card.change) return 'text-synrgy-muted'
    
    // For security metrics, "up" might be bad (more threats) or good (more detections)
    // We'll use the status to determine color
    switch (card.status) {
      case 'critical':
        return 'text-red-500'
      case 'warning':
        return 'text-synrgy-accent'
      default:
        switch (card.change.trend) {
          case 'up':
            return 'text-green-500'
          case 'down':
            return 'text-red-500'
          default:
            return 'text-synrgy-muted'
        }
    }
  }

  const getCardColor = () => {
    switch (card.color || card.status) {
      case 'danger':
      case 'critical':
        return 'border-red-500/30 bg-red-500/5'
      case 'warning':
        return 'border-synrgy-accent/30 bg-synrgy-accent/5'
      case 'accent':
        return 'border-synrgy-accent/30 bg-synrgy-accent/5'
      case 'primary':
      default:
        return 'border-synrgy-primary/20 bg-synrgy-surface/30'
    }
  }

  const handleAskSynrgy = () => {
    if (onAskSynrgy) {
      const context = `Tell me more about ${card.title.toLowerCase()}: currently ${card.value}${
        card.change ? `, ${card.change.trend} by ${Math.abs(card.change.value)}% ${card.change.period}` : ''
      }`
      onAskSynrgy(context)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, delay: index * 0.1, ease: "easeOut" }}
      className={`relative group ${className}`}
    >
      <div className={`
        ${getCardColor()} 
        border rounded-xl p-6 hover:border-synrgy-primary/40 
        transition-all duration-300 hover:-translate-y-1 hover:shadow-synrgy-glow/20
        cursor-pointer
      `}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-synrgy-primary rounded-full" />
            <h3 className="text-sm font-medium text-synrgy-muted">{card.title}</h3>
          </div>
          
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onAskSynrgy && (
              <button
                onClick={handleAskSynrgy}
                className="p-1.5 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
                title="Ask SYNRGY about this metric"
              >
                <MessageSquare className="w-4 h-4 text-synrgy-primary" />
              </button>
            )}
            
            <button className="p-1.5 hover:bg-synrgy-primary/10 rounded-lg transition-colors">
              <MoreVertical className="w-4 h-4 text-synrgy-muted" />
            </button>
          </div>
        </div>

        {/* Value */}
        <div className="mb-3">
          <div className="text-3xl font-bold text-synrgy-text leading-none">
            {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
          </div>
        </div>

        {/* Trend */}
        {card.change && (
          <div className={`flex items-center gap-2 text-sm ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="font-medium">
              {card.change.value > 0 ? '+' : ''}{card.change.value}%
            </span>
            <span className="text-synrgy-muted">
              vs {card.change.period}
            </span>
          </div>
        )}

        {/* Status indicator */}
        {card.status && card.status !== 'normal' && (
          <div className="absolute top-4 right-4">
            <div className={`w-2 h-2 rounded-full ${
              card.status === 'critical' ? 'bg-red-500' : 
              card.status === 'warning' ? 'bg-synrgy-accent' : 'bg-green-500'
            }`} />
          </div>
        )}

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-synrgy-primary/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      </div>

      {/* Ask SYNRGY tooltip */}
      {onAskSynrgy && (
        <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
          <div className="bg-synrgy-surface border border-synrgy-primary/20 rounded-lg px-3 py-2 text-xs text-synrgy-text whitespace-nowrap">
            Click to ask SYNRGY about this metric
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-synrgy-surface border-l border-t border-synrgy-primary/20 rotate-45" />
          </div>
        </div>
      )}
    </motion.div>
  )
}
