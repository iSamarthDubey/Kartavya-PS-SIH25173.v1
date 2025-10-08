import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Types
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sessionId: string;
  queryInfo?: {
    intent: string;
    entities: any[];
    siemQuery: any;
    executionTime: number;
    resultsCount: number;
  };
  results?: any[];
  isLoading?: boolean;
  error?: string;
}

interface ConversationContext {
  lastQuery?: string;
  lastIntent?: string;
  lastEntities?: any[];
  queryCount: number;
  sessionStarted: Date;
}

interface ChatStore {
  // State
  messages: Message[];
  activeSession: string;
  isTyping: boolean;
  isConnected: boolean;
  context: ConversationContext;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setTyping: (isTyping: boolean) => void;
  setConnected: (isConnected: boolean) => void;
  updateContext: (updates: Partial<ConversationContext>) => void;
  generateSessionId: () => string;
  
  // Getters
  getMessagesBySession: (sessionId?: string) => Message[];
  getLastUserMessage: () => Message | undefined;
  getLastAssistantMessage: () => Message | undefined;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // Initial State
      messages: [],
      activeSession: `session_${Date.now()}`,
      isTyping: false,
      isConnected: false,
      context: {
        queryCount: 0,
        sessionStarted: new Date(),
      },

      // Actions
      addMessage: (messageData) => {
        const message: Message = {
          ...messageData,
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        };

        set((state) => ({
          messages: [...state.messages, message],
          context: {
            ...state.context,
            queryCount: messageData.type === 'user' 
              ? state.context.queryCount + 1 
              : state.context.queryCount,
            lastQuery: messageData.type === 'user' 
              ? messageData.content 
              : state.context.lastQuery,
          }
        }));
      },

      updateMessage: (id, updates) => {
        set((state) => ({
          messages: state.messages.map(msg => 
            msg.id === id ? { ...msg, ...updates } : msg
          )
        }));
      },

      clearMessages: () => {
        set((state) => ({
          messages: [],
          context: {
            queryCount: 0,
            sessionStarted: new Date(),
          }
        }));
      },

      setTyping: (isTyping) => set({ isTyping }),
      
      setConnected: (isConnected) => set({ isConnected }),

      updateContext: (updates) => {
        set((state) => ({
          context: { ...state.context, ...updates }
        }));
      },

      generateSessionId: () => {
        const sessionId = `session_${Date.now()}`;
        set({ activeSession: sessionId });
        return sessionId;
      },

      // Getters
      getMessagesBySession: (sessionId) => {
        const state = get();
        const targetSession = sessionId || state.activeSession;
        return state.messages.filter(msg => msg.sessionId === targetSession);
      },

      getLastUserMessage: () => {
        const state = get();
        return [...state.messages]
          .reverse()
          .find(msg => msg.type === 'user');
      },

      getLastAssistantMessage: () => {
        const state = get();
        return [...state.messages]
          .reverse()
          .find(msg => msg.type === 'assistant');
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        messages: state.messages.slice(-50), // Keep only last 50 messages
        activeSession: state.activeSession,
        context: state.context,
      }),
    }
  )
);
