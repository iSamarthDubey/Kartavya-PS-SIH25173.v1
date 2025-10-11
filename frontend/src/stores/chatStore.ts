/**
 * Chat Store - Manages conversation state and chat history
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ChatMessage, ChatRequest, ConversationContext } from '@/types'
import { chatApi } from '@/services/api'
// Simple UUID generator for now
const uuidv4 = () => {
  return 'xxxx-xxxx-xxxx-xxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c == 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

interface ChatState {
  // Current conversation
  currentConversationId: string | null
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  
  // Context and state
  context: ConversationContext | null
  suggestions: string[]
  typing: boolean
  
  // UI state
  showExplainQuery: boolean
  selectedMessageId: string | null
  
  // Actions
  setCurrentConversation: (id: string) => void
  sendMessage: (request: ChatRequest) => Promise<void>
  addMessage: (message: ChatMessage) => void
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void
  clearError: () => void
  setTyping: (typing: boolean) => void
  toggleExplainQuery: () => void
  selectMessage: (messageId: string | null) => void
  
  // Context management
  updateContext: (updates: Partial<ConversationContext>) => void
  clearContext: () => void
  
  // Utility functions
  getMessagesForConversation: (conversationId: string) => ChatMessage[]
  getLastUserMessage: () => ChatMessage | null
  getLastAssistantMessage: () => ChatMessage | null
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentConversationId: null,
      messages: [],
      isLoading: false,
      error: null,
      context: null,
      suggestions: [],
      typing: false,
      showExplainQuery: false,
      selectedMessageId: null,

      // Actions
      setCurrentConversation: (id: string) => {
        set({ 
          currentConversationId: id,
          messages: get().getMessagesForConversation(id),
          error: null
        })
      },

      sendMessage: async (request: ChatRequest) => {
        const state = get()
        
        // Generate conversation ID if not provided
        const conversationId = request.conversation_id || state.currentConversationId || uuidv4()
        
        // Create user message
        const userMessage: ChatMessage = {
          id: uuidv4(),
          conversation_id: conversationId,
          role: 'user',
          content: request.query,
          timestamp: new Date().toISOString(),
          status: 'success'
        }

        // Create pending assistant message
        const assistantMessage: ChatMessage = {
          id: uuidv4(),
          conversation_id: conversationId,
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
          status: 'pending'
        }

        try {
          set({
            currentConversationId: conversationId,
            isLoading: true,
            error: null,
            typing: true
          })

          // Add user message and pending assistant message
          get().addMessage(userMessage)
          get().addMessage(assistantMessage)

          // Send request to API
          const response = await chatApi.sendMessage({
            ...request,
            conversation_id: conversationId
          })

          // Update assistant message with response
          get().updateMessage(assistantMessage.id, {
            content: response.summary,
            status: response.status as any,
            error: response.error,
            metadata: {
              intent: response.intent,
              confidence: response.confidence,
              processing_time: response.metadata?.processing_time,
              query_type: response.intent,
              total_results: response.results?.length || 0
            },
            visual_payload: response.visualizations ? {
              type: 'composite',
              cards: response.visualizations.map(viz => ({
                type: viz.type === 'time_series' ? 'chart' : viz.type as any,
                title: viz.title,
                data: viz.data,
                config: viz.config,
                chart_type: viz.config?.chart_type as any
              }))
            } : undefined
          })

          // Update context
          const newContext: ConversationContext = {
            conversation_id: conversationId,
            history: [...state.messages, userMessage, {
              ...assistantMessage,
              content: response.summary,
              status: response.status as any
            }].slice(-10), // Keep last 10 messages
            entities: response.entities.reduce((acc, entity) => {
              acc[entity.type] = acc[entity.type] || []
              acc[entity.type].push(entity.value)
              return acc
            }, {} as Record<string, any>),
            filters: [],
            metadata: response.metadata
          }

          set({
            context: newContext,
            suggestions: response.suggestions || [],
            typing: false,
            isLoading: false
          })

        } catch (error: any) {
          console.error('Failed to send message:', error)
          
          // Update assistant message with error
          get().updateMessage(assistantMessage.id, {
            content: 'I apologize, but I encountered an error processing your request. Please try again.',
            status: 'error',
            error: error.message || 'Unknown error occurred'
          })

          set({
            error: error.message || 'Failed to send message',
            typing: false,
            isLoading: false
          })
        }
      },

      addMessage: (message: ChatMessage) => {
        set(state => ({
          messages: [...state.messages, message]
        }))
      },

      updateMessage: (messageId: string, updates: Partial<ChatMessage>) => {
        set(state => ({
          messages: state.messages.map(msg => 
            msg.id === messageId 
              ? { ...msg, ...updates, timestamp: updates.timestamp || msg.timestamp }
              : msg
          )
        }))
      },

      clearMessages: () => {
        set({ 
          messages: [], 
          context: null, 
          suggestions: [],
          selectedMessageId: null,
          error: null
        })
      },

      clearError: () => {
        set({ error: null })
      },

      setTyping: (typing: boolean) => {
        set({ typing })
      },

      toggleExplainQuery: () => {
        set(state => ({ showExplainQuery: !state.showExplainQuery }))
      },

      selectMessage: (messageId: string | null) => {
        set({ selectedMessageId: messageId })
      },

      // Context management
      updateContext: (updates: Partial<ConversationContext>) => {
        set(state => ({
          context: state.context ? { ...state.context, ...updates } : null
        }))
      },

      clearContext: () => {
        set({ context: null })
      },

      // Utility functions
      getMessagesForConversation: (conversationId: string) => {
        return get().messages.filter(msg => msg.conversation_id === conversationId)
      },

      getLastUserMessage: () => {
        const messages = get().messages
        for (let i = messages.length - 1; i >= 0; i--) {
          if (messages[i].role === 'user') {
            return messages[i]
          }
        }
        return null
      },

      getLastAssistantMessage: () => {
        const messages = get().messages
        for (let i = messages.length - 1; i >= 0; i--) {
          if (messages[i].role === 'assistant') {
            return messages[i]
          }
        }
        return null
      }
    }),
    {
      name: 'synrgy-chat-store',
      partialize: (state) => ({
        // Only persist essential state
        currentConversationId: state.currentConversationId,
        messages: state.messages.slice(-50), // Only keep last 50 messages
        context: state.context,
        showExplainQuery: state.showExplainQuery
      })
    }
  )
)

// Selectors for better performance
export const useCurrentMessages = () => {
  const currentConversationId = useChatStore(state => state.currentConversationId)
  const messages = useChatStore(state => state.messages)
  
  return messages.filter(msg => 
    !currentConversationId || msg.conversation_id === currentConversationId
  )
}

export const useIsCurrentConversation = (conversationId: string) => {
  return useChatStore(state => state.currentConversationId === conversationId)
}

export const useChatLoading = () => {
  return useChatStore(state => state.isLoading || state.typing)
}
