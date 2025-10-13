import { create } from 'zustand'

interface ContextSyncState {
  // Sync state
  syncEnabled: boolean
  lastSyncTime: Date | null
  pendingSync: boolean

  // Context data
  dashboardContext: {
    activeWidgets: string[]
    selectedMetrics: string[]
    timeRange: { start: string; end: string }
    filters: Record<string, any>
  }

  chatContext: {
    activeConversation: string | null
    lastQuery: string | null
    querySource: 'user' | 'dashboard' | 'widget' | null
  }

  // Actions
  setSyncEnabled: (enabled: boolean) => void
  updateDashboardContext: (context: Partial<ContextSyncState['dashboardContext']>) => void
  updateChatContext: (context: Partial<ContextSyncState['chatContext']>) => void
  syncContexts: () => Promise<void>
  generateContextualQuery: (widget: string, metric: string) => string
}

const useContextSync = create<ContextSyncState>((set, get) => ({
  // Initial state
  syncEnabled: true,
  lastSyncTime: null,
  pendingSync: false,

  dashboardContext: {
    activeWidgets: [],
    selectedMetrics: [],
    timeRange: { start: '', end: '' },
    filters: {},
  },

  chatContext: {
    activeConversation: null,
    lastQuery: null,
    querySource: null,
  },

  // Actions
  setSyncEnabled: enabled => {
    set({ syncEnabled: enabled })
    if (enabled) {
      get().syncContexts()
    }
  },

  updateDashboardContext: context => {
    set(state => ({
      dashboardContext: {
        ...state.dashboardContext,
        ...context,
      },
    }))

    if (get().syncEnabled) {
      get().syncContexts()
    }
  },

  updateChatContext: context => {
    set(state => ({
      chatContext: {
        ...state.chatContext,
        ...context,
      },
    }))

    if (get().syncEnabled) {
      get().syncContexts()
    }
  },

  syncContexts: async () => {
    const state = get()
    if (state.pendingSync) return

    set({ pendingSync: true })

    try {
      // Simulate context sync processing
      await new Promise(resolve => setTimeout(resolve, 300))

      set({
        lastSyncTime: new Date(),
        pendingSync: false,
      })
    } catch (error) {
      console.error('Context sync failed:', error)
      set({ pendingSync: false })
    }
  },

  generateContextualQuery: (widget, metric) => {
    const state = get()
    // Access dashboardContext for potential future use
    state.dashboardContext

    // Generate intelligent queries based on widget and metric context
    const queries = {
      'threat-activity': {
        total_threats: `What are the main threat sources contributing to the ${metric} detected today?`,
        blocked_attempts: `Why are there ${metric} blocked attempts? Show me the attack patterns.`,
        high_severity: `Analyze the ${metric} high severity threats and their potential impact.`,
      },
      'top-threats': {
        malware: `Give me detailed analysis of the malware threats and recommended mitigation strategies.`,
        phishing: `What phishing campaigns are currently active and how can we better protect against them?`,
        ransomware: `Analyze the ransomware threat landscape and our current defense posture.`,
      },
      'geo-distribution': {
        attack_sources: `Which countries are the primary sources of attacks and what are their typical attack methods?`,
        target_locations: `Why are certain geographic regions being targeted more frequently?`,
      },
      'recent-activities': {
        security_events: `Explain the recent security events and their correlation with current threat intelligence.`,
        user_activities: `Are there any suspicious user activities that require immediate attention?`,
      },
    }

    // Get specific query or fallback to generic
    const widgetQueries = queries[widget as keyof typeof queries]
    if (widgetQueries && metric in widgetQueries) {
      return widgetQueries[metric as keyof typeof widgetQueries]
    }

    // Fallback contextual query
    return `Analyze the ${metric} metric from the ${widget} widget and provide insights with actionable recommendations.`
  },
}))

export { useContextSync }

// Context sync utilities
export const contextSyncUtils = {
  // Format context for chat queries
  formatDashboardContext: (context: ContextSyncState['dashboardContext']) => {
    return {
      active_widgets: context.activeWidgets,
      selected_metrics: context.selectedMetrics,
      time_range: context.timeRange,
      applied_filters: context.filters,
      dashboard_state: 'hybrid_mode',
    }
  },

  // Extract relevant context from chat for dashboard
  extractChatContext: (messages: any[]) => {
    const recentMessage = messages[messages.length - 1]

    return {
      recent_query: recentMessage?.content,
      query_type: recentMessage?.metadata?.query_type,
      referenced_entities: recentMessage?.entities || [],
      conversation_topic: messages
        .map(m => m.content)
        .join(' ')
        .slice(0, 100),
    }
  },

  // Generate sync status message
  getSyncStatus: (state: ContextSyncState) => {
    if (!state.syncEnabled) return 'Sync Disabled'
    if (state.pendingSync) return 'Syncing...'
    if (state.lastSyncTime) {
      const timeDiff = Date.now() - state.lastSyncTime.getTime()
      const minutes = Math.floor(timeDiff / 60000)
      return minutes === 0 ? 'Just synced' : `Synced ${minutes}m ago`
    }
    return 'Not synced'
  },
}

// Context sync hooks
export const useContextualQuery = () => {
  const { generateContextualQuery, updateChatContext } = useContextSync()

  return {
    generateQuery: (widget: string, metric: string) => {
      const query = generateContextualQuery(widget, metric)
      updateChatContext({
        lastQuery: query,
        querySource: 'dashboard',
      })
      return query
    },
  }
}

export const useDashboardSync = () => {
  const { updateDashboardContext, dashboardContext } = useContextSync()

  return {
    updateActiveWidgets: (widgets: string[]) => {
      updateDashboardContext({ activeWidgets: widgets })
    },
    updateMetrics: (metrics: string[]) => {
      updateDashboardContext({ selectedMetrics: metrics })
    },
    updateTimeRange: (start: string, end: string) => {
      updateDashboardContext({ timeRange: { start, end } })
    },
    updateFilters: (filters: Record<string, any>) => {
      updateDashboardContext({ filters })
    },
    context: dashboardContext,
  }
}
