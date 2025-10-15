/**
 * SYNRGY Chat Commands & Conversational Flow
 * Intelligent command suggestions and contextual interactions
 */

import React, { useState, useRef, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Command,
  Search,
  ChevronRight,
  Lightbulb,
  Shield,
  BarChart3,
  Network,
  Users,
  Clock,
  AlertTriangle,
  Database,
  TrendingUp,
  Map,
  Activity,
  Filter,
  Download,
  Share,
  BookOpen,
  Zap,
  Target,
  Globe,
  Lock
} from 'lucide-react'

import { 
  AnimatedCard,
  TouchButton,
  useBreakpoint,
  Tooltip
} from '@/components/UI'

interface ChatCommand {
  id: string
  category: string
  icon: React.ComponentType<any>
  label: string
  description: string
  template: string
  keywords: string[]
  examples?: string[]
  requiresParams?: boolean
}

interface CommandSuggestionProps {
  onSelectCommand: (command: string) => void
  currentInput: string
  recentCommands?: string[]
  className?: string
}

interface ConversationContextProps {
  lastMessage?: any
  sessionTopic?: string
  suggestedFollowups?: string[]
  onFollowup: (query: string) => void
}

// Predefined command categories and commands
const COMMAND_CATEGORIES = {
  THREAT_ANALYSIS: {
    label: 'Threat Analysis',
    icon: Shield,
    color: 'text-red-500'
  },
  SECURITY_MONITORING: {
    label: 'Security Monitoring',
    icon: Activity,
    color: 'text-orange-500'
  },
  DATA_INVESTIGATION: {
    label: 'Data Investigation',
    icon: Search,
    color: 'text-blue-500'
  },
  REPORTING: {
    label: 'Reporting',
    icon: BarChart3,
    color: 'text-green-500'
  },
  NETWORK_ANALYSIS: {
    label: 'Network Analysis',
    icon: Network,
    color: 'text-purple-500'
  },
  COMPLIANCE: {
    label: 'Compliance',
    icon: Lock,
    color: 'text-yellow-500'
  }
}

const CHAT_COMMANDS: ChatCommand[] = [
  // Threat Analysis
  {
    id: 'show-recent-threats',
    category: 'THREAT_ANALYSIS',
    icon: Shield,
    label: 'Show Recent Threats',
    description: 'Display recent security threats and incidents',
    template: 'Show me recent threats from the last {timeframe}',
    keywords: ['threat', 'recent', 'attack', 'malware', 'incident'],
    examples: ['Show me recent threats from the last 24 hours', 'Recent threats this week']
  },
  {
    id: 'threat-intelligence',
    category: 'THREAT_ANALYSIS',
    icon: Target,
    label: 'Threat Intelligence',
    description: 'Get threat intelligence and IOCs',
    template: 'Analyze threat intelligence for {indicator_type}',
    keywords: ['intelligence', 'ioc', 'indicator', 'reputation'],
    examples: ['Analyze threat intelligence for IP 192.168.1.100', 'Check domain reputation']
  },
  {
    id: 'malware-analysis',
    category: 'THREAT_ANALYSIS',
    icon: AlertTriangle,
    label: 'Malware Analysis',
    description: 'Analyze malware samples and signatures',
    template: 'Analyze malware samples {hash_or_signature}',
    keywords: ['malware', 'virus', 'hash', 'signature', 'analyze'],
    examples: ['Analyze malware samples from today', 'Check hash reputation']
  },

  // Security Monitoring
  {
    id: 'security-alerts',
    category: 'SECURITY_MONITORING',
    icon: AlertTriangle,
    label: 'Security Alerts',
    description: 'View and manage security alerts',
    template: 'Show security alerts {severity} {timeframe}',
    keywords: ['alert', 'security', 'warning', 'critical', 'high'],
    examples: ['Show high severity alerts today', 'Critical alerts this week']
  },
  {
    id: 'system-health',
    category: 'SECURITY_MONITORING',
    icon: Activity,
    label: 'System Health',
    description: 'Check overall security posture and system health',
    template: 'Show system health dashboard',
    keywords: ['health', 'status', 'posture', 'overview', 'dashboard'],
    examples: ['Show system health dashboard', 'Security posture overview']
  },
  {
    id: 'failed-logins',
    category: 'SECURITY_MONITORING',
    icon: Users,
    label: 'Failed Logins',
    description: 'Analyze failed login attempts and patterns',
    template: 'Show failed login attempts {timeframe} {user_or_source}',
    keywords: ['login', 'failed', 'authentication', 'brute', 'force'],
    examples: ['Failed login attempts today', 'Brute force attacks this week']
  },

  // Data Investigation
  {
    id: 'log-search',
    category: 'DATA_INVESTIGATION',
    icon: Search,
    label: 'Log Search',
    description: 'Search through security logs and events',
    template: 'Search logs for {query} in {timeframe}',
    keywords: ['search', 'logs', 'events', 'find', 'query'],
    examples: ['Search logs for failed SSH attempts', 'Find events with source IP']
  },
  {
    id: 'user-activity',
    category: 'DATA_INVESTIGATION',
    icon: Users,
    label: 'User Activity',
    description: 'Investigate user behavior and activities',
    template: 'Show user activity for {username} {timeframe}',
    keywords: ['user', 'activity', 'behavior', 'actions', 'timeline'],
    examples: ['Show user activity for admin today', 'User behavior analysis']
  },
  {
    id: 'network-traffic',
    category: 'DATA_INVESTIGATION',
    icon: Network,
    label: 'Network Traffic',
    description: 'Analyze network traffic patterns and anomalies',
    template: 'Analyze network traffic {direction} {timeframe}',
    keywords: ['network', 'traffic', 'bandwidth', 'flow', 'connection'],
    examples: ['Analyze outbound network traffic', 'Network connections to external IPs']
  },

  // Reporting
  {
    id: 'security-report',
    category: 'REPORTING',
    icon: BarChart3,
    label: 'Security Report',
    description: 'Generate comprehensive security reports',
    template: 'Generate security report for {timeframe}',
    keywords: ['report', 'summary', 'statistics', 'metrics', 'kpi'],
    examples: ['Generate weekly security report', 'Monthly threat summary']
  },
  {
    id: 'compliance-status',
    category: 'COMPLIANCE',
    icon: Lock,
    label: 'Compliance Status',
    description: 'Check compliance with security frameworks',
    template: 'Show compliance status for {framework}',
    keywords: ['compliance', 'framework', 'audit', 'regulation', 'standard'],
    examples: ['Show NIST compliance status', 'ISO 27001 audit results']
  },
  {
    id: 'trend-analysis',
    category: 'REPORTING',
    icon: TrendingUp,
    label: 'Trend Analysis',
    description: 'Analyze security trends and patterns over time',
    template: 'Show {metric} trends over {timeframe}',
    keywords: ['trend', 'pattern', 'analysis', 'overtime', 'comparison'],
    examples: ['Show alert trends over last month', 'Attack pattern analysis']
  }
]

// Command Suggestion Component
export const CommandSuggestions: React.FC<CommandSuggestionProps> = ({
  onSelectCommand,
  currentInput,
  recentCommands = [],
  className = ''
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const { isMobile } = useBreakpoint()

  // Filter commands based on input and search
  const filteredCommands = useMemo(() => {
    let commands = CHAT_COMMANDS

    // Filter by category
    if (selectedCategory !== 'all') {
      commands = commands.filter(cmd => cmd.category === selectedCategory)
    }

    // Filter by search query or current input
    const query = searchQuery || currentInput.toLowerCase()
    if (query) {
      commands = commands.filter(cmd =>
        cmd.label.toLowerCase().includes(query) ||
        cmd.description.toLowerCase().includes(query) ||
        cmd.keywords.some(keyword => keyword.includes(query)) ||
        cmd.template.toLowerCase().includes(query)
      )
    }

    return commands
  }, [selectedCategory, searchQuery, currentInput])

  // Get suggested commands based on context
  const contextualSuggestions = useMemo(() => {
    if (currentInput.length < 3) return []
    
    return filteredCommands.slice(0, 5)
  }, [filteredCommands, currentInput])

  const handleCommandSelect = (command: ChatCommand) => {
    onSelectCommand(command.template)
  }

  const handleExampleSelect = (example: string) => {
    onSelectCommand(example)
  }

  return (
    <AnimatedCard className={`${className} bg-synrgy-surface border border-synrgy-primary/20`}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <Command className="w-5 h-5 text-synrgy-primary" />
          <h3 className="font-semibold text-synrgy-text">Command Suggestions</h3>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
          <input
            type="text"
            placeholder="Search commands..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-synrgy-bg-950 border border-synrgy-primary/20 rounded-lg text-synrgy-text placeholder:text-synrgy-muted focus:outline-none focus:ring-2 focus:ring-synrgy-primary"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-4">
          <TouchButton
            variant={selectedCategory === 'all' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setSelectedCategory('all')}
            className="text-xs"
          >
            All
          </TouchButton>
          {Object.entries(COMMAND_CATEGORIES).map(([key, category]) => (
            <TouchButton
              key={key}
              variant={selectedCategory === key ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setSelectedCategory(key)}
              className="text-xs"
            >
              <category.icon className="w-3 h-3 mr-1" />
              {category.label}
            </TouchButton>
          ))}
        </div>

        {/* Recent Commands */}
        {recentCommands.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-synrgy-muted mb-2">Recent</h4>
            <div className="space-y-1">
              {recentCommands.slice(0, 3).map((command, index) => (
                <TouchButton
                  key={index}
                  variant="ghost"
                  className="w-full justify-start text-left text-sm p-2 hover:bg-synrgy-primary/5"
                  onClick={() => onSelectCommand(command)}
                >
                  <Clock className="w-3 h-3 mr-2 text-synrgy-muted" />
                  <span className="truncate">{command}</span>
                </TouchButton>
              ))}
            </div>
          </div>
        )}

        {/* Contextual Suggestions */}
        {contextualSuggestions.length > 0 && currentInput && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-synrgy-muted mb-2">Suggestions</h4>
            <div className="space-y-2">
              {contextualSuggestions.map((command) => (
                <motion.div
                  key={command.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-synrgy-bg-950/50 rounded-lg p-3 border border-synrgy-primary/10 hover:border-synrgy-primary/20 transition-colors cursor-pointer"
                  onClick={() => handleCommandSelect(command)}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <command.icon className="w-4 h-4 text-synrgy-primary" />
                    <span className="font-medium text-synrgy-text text-sm">{command.label}</span>
                  </div>
                  <p className="text-xs text-synrgy-muted mb-2">{command.description}</p>
                  <code className="text-xs bg-synrgy-bg-900 text-synrgy-accent px-2 py-1 rounded">
                    {command.template}
                  </code>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* All Commands */}
        <div className="space-y-3">
          {Object.entries(COMMAND_CATEGORIES).map(([categoryKey, category]) => {
            const categoryCommands = filteredCommands.filter(cmd => cmd.category === categoryKey)
            if (categoryCommands.length === 0 || (selectedCategory !== 'all' && selectedCategory !== categoryKey)) return null

            return (
              <div key={categoryKey}>
                <div className="flex items-center gap-2 mb-2">
                  <category.icon className={`w-4 h-4 ${category.color}`} />
                  <h4 className="text-sm font-medium text-synrgy-text">{category.label}</h4>
                </div>
                <div className="space-y-2 ml-6">
                  {categoryCommands.map((command) => (
                    <div key={command.id} className="space-y-2">
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="bg-synrgy-bg-950/30 rounded-lg p-3 border border-synrgy-primary/10 hover:border-synrgy-primary/20 transition-colors cursor-pointer"
                        onClick={() => handleCommandSelect(command)}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-synrgy-text text-sm">{command.label}</span>
                          <ChevronRight className="w-3 h-3 text-synrgy-muted" />
                        </div>
                        <p className="text-xs text-synrgy-muted mb-2">{command.description}</p>
                        <code className="text-xs bg-synrgy-bg-900 text-synrgy-accent px-2 py-1 rounded block">
                          {command.template}
                        </code>
                      </motion.div>

                      {/* Examples */}
                      {command.examples && command.examples.length > 0 && (
                        <div className="ml-4 space-y-1">
                          {command.examples.map((example, idx) => (
                            <TouchButton
                              key={idx}
                              variant="ghost"
                              size="sm"
                              className="w-full justify-start text-left text-xs p-2 text-synrgy-muted hover:text-synrgy-text"
                              onClick={() => handleExampleSelect(example)}
                            >
                              <Lightbulb className="w-3 h-3 mr-2" />
                              {example}
                            </TouchButton>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </AnimatedCard>
  )
}

// Conversational Context Component
export const ConversationContext: React.FC<ConversationContextProps> = ({
  lastMessage,
  sessionTopic,
  suggestedFollowups = [],
  onFollowup
}) => {
  if (!lastMessage && !sessionTopic && suggestedFollowups.length === 0) {
    return null
  }

  // Generate contextual follow-up suggestions
  const contextualFollowups = useMemo(() => {
    const followups: string[] = [...suggestedFollowups]

    // Add contextual suggestions based on last message
    if (lastMessage?.content) {
      const content = lastMessage.content.toLowerCase()
      
      if (content.includes('alert') || content.includes('threat')) {
        followups.push(
          'Show me more details about these alerts',
          'What are the recommended actions?',
          'Are there any related incidents?'
        )
      }
      
      if (content.includes('user') || content.includes('login')) {
        followups.push(
          'Show user activity timeline',
          'Check for other suspicious accounts',
          'What are the normal login patterns?'
        )
      }
      
      if (content.includes('network') || content.includes('traffic')) {
        followups.push(
          'Analyze traffic patterns over time',
          'Show top communicating hosts',
          'Are there any blocked connections?'
        )
      }
    }

    return followups.slice(0, 6) // Limit to 6 suggestions
  }, [lastMessage, suggestedFollowups])

  return (
    <AnimatedCard className="bg-synrgy-surface/30 border border-synrgy-primary/10">
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Lightbulb className="w-4 h-4 text-synrgy-accent" />
          <h4 className="text-sm font-medium text-synrgy-text">Follow up questions</h4>
        </div>

        {sessionTopic && (
          <div className="mb-3 p-2 bg-synrgy-primary/5 rounded-lg border border-synrgy-primary/10">
            <p className="text-xs text-synrgy-muted">Current topic:</p>
            <p className="text-sm text-synrgy-text font-medium">{sessionTopic}</p>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {contextualFollowups.map((followup, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onFollowup(followup)}
              className="text-xs px-3 py-2 bg-synrgy-bg-950/50 border border-synrgy-primary/20 rounded-full text-synrgy-text hover:bg-synrgy-primary/10 hover:border-synrgy-primary/30 transition-colors"
            >
              {followup}
            </motion.button>
          ))}
        </div>
      </div>
    </AnimatedCard>
  )
}

export default { CommandSuggestions, ConversationContext }
