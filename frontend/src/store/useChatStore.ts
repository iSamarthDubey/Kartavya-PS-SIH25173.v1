import { create } from 'zustand'

export type ChatSender = 'user' | 'ai'

export type ChatMessage = {
  sender: ChatSender
  text: string
}

type ChatStore = {
  messages: ChatMessage[]
  addMessage: (msg: ChatMessage) => void
  clearChat: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  clearChat: () => set({ messages: [] }),
}))
