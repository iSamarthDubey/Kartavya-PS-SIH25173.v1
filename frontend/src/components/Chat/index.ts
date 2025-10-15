/**
 * SYNRGY Enhanced Chat Components
 * Export all chat-related components and utilities
 */

// Main Chat Components
export { EnhancedChatInterface } from './EnhancedChatInterface'
export { default as EnhancedChatInput } from './EnhancedChatInput'
export { SynrgyChatLayout, FloatingChatButton } from './SynrgyChatLayout'

// Command and Conversation Components
export { CommandSuggestions, ConversationContext } from './ChatCommands'

// Visual Components (re-export from existing)
export { VisualRenderer } from './VisualRenderer'
export { EnhancedVisualRenderer } from './EnhancedVisualRenderer'

// Types and utilities
export type {
  ChatMessage,
  VisualPayload,
  StreamingChatResponse,
} from '@/types'

// Default exports for convenience
export { EnhancedChatInterface as ChatInterface }
export { SynrgyChatLayout as ChatLayout }
export { EnhancedChatInput as ChatInput }
export { CommandSuggestions as Commands }
export { ConversationContext as Context }

// Re-export visual performance components if they exist
export * from './VisualPerformance'
