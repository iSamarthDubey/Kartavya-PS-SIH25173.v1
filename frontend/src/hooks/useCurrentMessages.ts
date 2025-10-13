/**
 * Hook to get current messages for active conversation
 */

import { useMemo } from 'react'
import { useChatStore } from '@/stores/chatStore'

export function useCurrentMessages() {
  const { messages, currentConversationId } = useChatStore()

  return useMemo(() => {
    if (!currentConversationId) {
      return messages // Return all messages if no specific conversation
    }

    // Filter messages for current conversation
    return messages.filter(message => message.conversation_id === currentConversationId)
  }, [messages, currentConversationId])
}
