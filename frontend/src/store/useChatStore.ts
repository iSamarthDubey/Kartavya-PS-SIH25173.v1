import { create } from 'zustand';

interface MessageMetadata {
  intent?: string;
  confidence?: number;
  entities?: Record<string, any>;
  query?: {
    dsl: any;
    index: string;
  };
  results_count?: number;
  execution_time?: number;
  platform?: string;
}

interface Message {
  sender: 'user' | 'ai';
  text: string;
  timestamp?: string;
  metadata?: MessageMetadata;
  isError?: boolean;
  id?: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  
  // Message operations
  addMessage: (message: Omit<Message, 'id'>) => void;
  clearMessages: () => void;
  
  // Loading state
  setLoading: (loading: boolean) => void;
}

const generateId = () => Math.random().toString(36).substring(2, 15);

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,

  addMessage: (message) => {
    const messageWithId: Message = {
      ...message,
      id: generateId(),
      timestamp: message.timestamp || new Date().toISOString(),
    };
    
    set((state) => ({
      messages: [...state.messages, messageWithId],
    }));
  },

  clearMessages: () => set({ messages: [] }),

  setLoading: (loading) => set({ isLoading: loading }),
}));
