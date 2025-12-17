import { create } from 'zustand'
import { Conversation, Message, ConversationCreate } from '../types'
import { conversationService } from '../services'

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  isSending: boolean
  error: string | null

  // Actions
  fetchConversations: () => Promise<void>
  selectConversation: (id: number) => Promise<void>
  createConversation: (data: ConversationCreate) => Promise<Conversation>
  updateConversation: (id: number, title: string) => Promise<void>
  deleteConversation: (id: number) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  sendMessageStream: (content: string, onChunk: (chunk: string) => void) => Promise<void>
  deleteMessage: (messageId: number, deleteSubsequent: boolean) => Promise<void>
  clearError: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  fetchConversations: async () => {
    set({ isLoading: true, error: null })
    try {
      const conversations = await conversationService.getConversations()
      set({ conversations, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch conversations',
        isLoading: false,
      })
    }
  },

  selectConversation: async (id: number) => {
    set({ isLoading: true, error: null })
    try {
      const conversation = await conversationService.getConversation(id)
      const messages = await conversationService.getMessages(id)
      set({
        currentConversation: conversation,
        messages,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load conversation',
        isLoading: false,
      })
    }
  },

  createConversation: async (data: ConversationCreate) => {
    set({ isLoading: true, error: null })
    try {
      const conversation = await conversationService.createConversation(data)
      set((state) => ({
        conversations: [conversation, ...state.conversations],
        currentConversation: conversation,
        messages: [],
        isLoading: false,
      }))
      return conversation
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create conversation',
        isLoading: false,
      })
      throw error
    }
  },

  updateConversation: async (id: number, title: string) => {
    try {
      const updated = await conversationService.updateConversation(id, { title })
      set((state) => ({
        conversations: state.conversations.map((c) =>
          c.id === id ? updated : c
        ),
        currentConversation:
          state.currentConversation?.id === id
            ? updated
            : state.currentConversation,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update conversation',
      })
      throw error
    }
  },

  deleteConversation: async (id: number) => {
    try {
      await conversationService.deleteConversation(id)
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== id),
        currentConversation:
          state.currentConversation?.id === id ? null : state.currentConversation,
        messages: state.currentConversation?.id === id ? [] : state.messages,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete conversation',
      })
      throw error
    }
  },

  sendMessage: async (content: string) => {
    const { currentConversation } = get()
    if (!currentConversation) return

    set({ isSending: true, error: null })
    try {
      const response = await conversationService.sendMessage(
        currentConversation.id,
        { message: content }
      )

      set((state) => ({
        messages: [...state.messages, response.message],
        isSending: false,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isSending: false,
      })
      throw error
    }
  },

  sendMessageStream: async (content: string, onChunk: (chunk: string) => void) => {
    const { currentConversation } = get()
    if (!currentConversation) return

    set({ isSending: true, error: null })

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now(), // Temporary ID
      conversation_id: currentConversation.id,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    set((state) => ({
      messages: [...state.messages, userMessage],
    }))

    try {
      await conversationService.sendMessageStream(
        currentConversation.id,
        { message: content },
        onChunk,
        (response) => {
          // Replace user message and add assistant message
          set((state) => ({
            messages: [
              ...state.messages.filter((m) => m.id !== userMessage.id),
              response.message,
            ],
            isSending: false,
          }))
        },
        (error) => {
          set({
            error: error.message || 'Failed to send message',
            isSending: false,
          })
        }
      )
    } catch (error: any) {
      set({
        error: error.message || 'Failed to send message',
        isSending: false,
      })
    }
  },

  deleteMessage: async (messageId: number, deleteSubsequent: boolean) => {
    try {
      await conversationService.deleteMessage(messageId, deleteSubsequent)

      if (deleteSubsequent) {
        // Remove message and all subsequent messages
        set((state) => {
          const messageIndex = state.messages.findIndex((m) => m.id === messageId)
          if (messageIndex === -1) return state

          return {
            messages: state.messages.slice(0, messageIndex),
          }
        })
      } else {
        // Remove only this message
        set((state) => ({
          messages: state.messages.filter((m) => m.id !== messageId),
        }))
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete message',
      })
      throw error
    }
  },

  clearError: () => set({ error: null }),
}))
