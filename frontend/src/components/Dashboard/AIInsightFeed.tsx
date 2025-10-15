/**
 * SYNRGY AI Insight Feed Component
 * Implements SYNRGY.TXT specification: Right column AI Insight Feed with "Ask CYNRGY" buttons
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Shield,
  MessageCircle,
  ChevronRight,
  Sparkles,
  Clock,
  Target,
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { useNavigate } from 'react-router-dom'

interface AIInsightFeedProps {
  className?: string
}

interface InsightCard {
  id: string
  type: 'threat_detected' | 'anomaly' | 'recommendation' | 'trend_analysis' | 'security_tip'
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
  suggestedQuery?: string
  metadata?: Record<string, any>
}

// Mock insights - in real implementation, these would come from backend AI analysis
const mockInsights: InsightCard[] = [
  {
    id: '1',
    type: 'threat_detected',
    title: 'Unusual Login Pattern Detected',
    description: 'Multiple failed login attempts from external IPs in the last hour',
    priority: 'high',
    timestamp: '2 minutes ago',
    suggestedQuery: 'Show me failed login attempts from external IPs in the last hour'
  },
  {
    id: '2', 
    type: 'anomaly',
    title: 'Network Traffic Spike',
    description: 'Outbound traffic to external domains increased by 340%',
    priority: 'medium',
    timestamp: '5 minutes ago',
    suggestedQuery: 'Investigate outbound network traffic spikes'
  },
  {
    id: '3',
    type: 'recommendation',
    title: 'Suggested Investigation',
    description: 'Review Windows authentication events for privilege escalation patterns',
    priority: 'medium',
    timestamp: '12 minutes ago',
    suggestedQuery: 'Find Windows privilege escalation attempts'
  },
  {
    id: '4',
    type: 'trend_analysis',
    title: 'Weekly Security Trend',
    description: 'Malware detection rate decreased 23% this week - investigate if tools need updates',
    priority: 'low',
    timestamp: '1 hour ago',
    suggestedQuery: 'Show malware detection trends for the past week'
  }
]

const getInsightIcon = (type: InsightCard['type']) => {
  switch (type) {
    case 'threat_detected':
      return <AlertTriangle className="w-4 h-4" />
    case 'anomaly':
      return <TrendingUp className="w-4 h-4" />
    case 'recommendation':
      return <Target className="w-4 h-4" />
    case 'trend_analysis':
      return <Brain className="w-4 h-4" />
    case 'security_tip':
      return <Shield className="w-4 h-4" />
    default:
      return <Sparkles className="w-4 h-4" />
  }
}

const getPriorityColor = (priority: InsightCard['priority']) => {
  switch (priority) {
    case 'critical':
      return 'border-red-500/40 bg-red-500/10 text-red-400'
    case 'high':
      return 'border-orange-500/40 bg-orange-500/10 text-orange-400'
    case 'medium':
      return 'border-yellow-500/40 bg-yellow-500/10 text-yellow-400'
    case 'low':
      return 'border-synrgy-primary/40 bg-synrgy-primary/10 text-synrgy-primary'
    default:
      return 'border-synrgy-primary/40 bg-synrgy-primary/10 text-synrgy-primary'
  }
}

export default function AIInsightFeed({ className = '' }: AIInsightFeedProps) {
  const { setMode, setChatPanelOpen } = useAppStore()
  const navigate = useNavigate()
  const [insights] = useState<InsightCard[]>(mockInsights)

  const handleAskCYNRGY = (insight: InsightCard) => {
    if (insight.suggestedQuery) {
      // Switch to hybrid mode and open chat with the suggested query
      setMode('hybrid')
      setChatPanelOpen(true)
      navigate('/app/hybrid', { 
        state: { 
          initialQuery: insight.suggestedQuery,
          context: {
            source: 'ai_insight',
            insight_id: insight.id,
            insight_type: insight.type
          }
        } 
      })
    }
  }

  return (
    <div className={`w-80 bg-synrgy-surface/30 border-l border-synrgy-primary/10 flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-synrgy-primary/10">
        <div className="flex items-center gap-2 mb-2">
          <Brain className="w-5 h-5 text-synrgy-primary" />
          <h2 className="text-lg font-semibold text-synrgy-text">AI Insights</h2>
        </div>
        <p className="text-sm text-synrgy-muted">
          Smart recommendations from CYNRGY AI
        </p>
      </div>

      {/* Insights List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {insights.map((insight, index) => (
          <motion.div
            key={insight.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={`group border rounded-xl p-4 transition-all duration-200 hover:shadow-lg cursor-pointer ${
              getPriorityColor(insight.priority)
            }`}
            onClick={() => handleAskCYNRGY(insight)}
          >
            {/* Insight Header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {getInsightIcon(insight.type)}
                <div className="text-xs font-medium uppercase tracking-wide opacity-80">
                  {insight.type.replace('_', ' ')}
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs opacity-60">
                <Clock className="w-3 h-3" />
                {insight.timestamp}
              </div>
            </div>

            {/* Insight Content */}
            <div className="mb-3">
              <h3 className="font-semibold text-sm mb-1 group-hover:text-current transition-colors">
                {insight.title}
              </h3>
              <p className="text-xs opacity-90 leading-relaxed">
                {insight.description}
              </p>
            </div>

            {/* Ask CYNRGY Button */}
            <div className="flex items-center justify-between">
              <div className={`text-xs px-2 py-1 rounded-full font-medium ${
                insight.priority === 'critical' ? 'bg-red-500/20 text-red-300' :
                insight.priority === 'high' ? 'bg-orange-500/20 text-orange-300' :
                insight.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                'bg-synrgy-primary/20 text-synrgy-primary'
              }`}>
                {insight.priority.toUpperCase()}
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleAskCYNRGY(insight)
                }}
                className="flex items-center gap-1 px-3 py-1.5 bg-current/10 hover:bg-current/20 rounded-lg text-xs font-medium transition-colors group-hover:scale-105"
              >
                <MessageCircle className="w-3 h-3" />
                <span>Ask CYNRGY</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-synrgy-primary/10">
        <button className="w-full text-sm text-synrgy-muted hover:text-synrgy-text transition-colors">
          View all insights
        </button>
      </div>
    </div>
  )
}
