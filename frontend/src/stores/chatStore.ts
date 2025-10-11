/**
 * SYNRGY Chat Store - Clean SIEM Assistant implementation
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ChatMessage, ChatRequest, ConversationContext } from '@/types'
import { chatApi } from '@/services/api'

// Simple UUID generator
const uuidv4 = () => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
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
        
        try {
          set({
            currentConversationId: conversationId,
            isLoading: true,
            error: null,
            typing: true
          })

          // Add user message immediately
          const userMessage: ChatMessage = {
            id: uuidv4(),
            conversation_id: conversationId,
            role: 'user',
            content: request.query,
            timestamp: new Date().toISOString(),
            status: 'success'
          }
          get().addMessage(userMessage)

          // Send request to SIEM backend (auto-detects platform)
          const response = await chatApi.sendMessage({
            ...request,
            conversation_id: conversationId
          })

          // Add assistant response message
          const assistantMessage: ChatMessage = {
            id: uuidv4(),
            conversation_id: conversationId,
            role: 'assistant',
            content: response.summary || 'I processed your security query.',
            timestamp: new Date().toISOString(),
            status: response.status === 'success' ? 'success' : 'error',
            error: response.error,
            metadata: {
              intent: response.intent,
              confidence: response.confidence,
              query_type: response.intent,
              results_count: Object.keys(response.results || {}).length
            }
          }
          get().addMessage(assistantMessage)

          // Update context (simplified)
          const newContext: ConversationContext = {
            conversation_id: conversationId,
            history: [userMessage, assistantMessage],
            entities: {},
            filters: [],
            metadata: response.metadata || {}
          }

          set({
            context: newContext,
            suggestions: response.suggestions || [],
            typing: false,
            isLoading: false
          })

        } catch (error: any) {
          console.error('Failed to send message:', error)
          
          // Add error message
          const errorMessage: ChatMessage = {
            id: uuidv4(),
            conversation_id: conversationId,
            role: 'assistant',
            content: 'I encountered an error processing your security query. Please try again.',
            timestamp: new Date().toISOString(),
            status: 'error',
            error: error.message || 'Unknown error occurred'
          }
          get().addMessage(errorMessage)

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
