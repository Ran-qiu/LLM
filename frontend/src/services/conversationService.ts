import api from './api'
import {
  Conversation,
  ConversationCreate,
  ConversationUpdate,
  Message,
  ChatMessage,
  ChatResponse,
  SearchParams,
  SearchResult,
  PaginationParams,
} from '../types'

export const conversationService = {
  // Get all conversations
  getConversations: async (params?: PaginationParams) => {
    const response = await api.get<Conversation[]>('/chat/conversations', { params })
    return response.data
  },

  // Get conversation by ID
  getConversation: async (id: number) => {
    const response = await api.get<Conversation>(`/chat/conversations/${id}`)
    return response.data
  },

  // Create new conversation
  createConversation: async (data: ConversationCreate) => {
    const response = await api.post<Conversation>('/chat/conversations', data)
    return response.data
  },

  // Update conversation
  updateConversation: async (id: number, data: ConversationUpdate) => {
    const response = await api.put<Conversation>(`/chat/conversations/${id}`, data)
    return response.data
  },

  // Delete conversation
  deleteConversation: async (id: number) => {
    await api.delete(`/chat/conversations/${id}`)
  },

  // Get messages for a conversation
  getMessages: async (conversationId: number, params?: PaginationParams) => {
    const response = await api.get<Message[]>(`/chat/conversations/${conversationId}/messages`, { params })
    return response.data
  },

  // Send message
  sendMessage: async (conversationId: number, message: ChatMessage) => {
    const response = await api.post<ChatResponse>(`/chat/conversations/${conversationId}/messages`, message)
    return response.data
  },

  // Send message with streaming
  sendMessageStream: async (
    conversationId: number,
    message: ChatMessage,
    onChunk: (chunk: string) => void,
    onComplete: (response: ChatResponse) => void,
    onError: (error: Error) => void
  ) => {
    try {
      const response = await fetch(`/api/v1/chat/conversations/${conversationId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(message),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''
      let fullContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              continue
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullContent += parsed.content
                onChunk(parsed.content)
              }
              if (parsed.done) {
                onComplete(parsed)
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      onError(error as Error)
    }
  },

  // Edit message
  editMessage: async (messageId: number, content: string) => {
    const response = await api.put<Message>(`/chat/messages/${messageId}`, null, {
      params: { content },
    })
    return response.data
  },

  // Delete message
  deleteMessage: async (messageId: number, deleteSubsequent: boolean = false) => {
    await api.delete(`/chat/messages/${messageId}`, {
      params: { delete_subsequent: deleteSubsequent },
    })
  },

  // Regenerate response
  regenerateResponse: async (messageId: number) => {
    const response = await api.post<ChatResponse>(`/chat/messages/${messageId}/regenerate`)
    return response.data
  },

  // Search messages
  searchMessages: async (params: SearchParams) => {
    const response = await api.get<SearchResult[]>('/chat/search', { params })
    return response.data
  },

  // Export conversation
  exportConversation: async (conversationId: number, format: 'json' | 'markdown') => {
    const response = await api.get(`/chat/conversations/${conversationId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },

  // Add tag to conversation
  addTag: async (conversationId: number, tagId: number) => {
    await api.post(`/chat/conversations/${conversationId}/tags/${tagId}`)
  },

  // Remove tag from conversation
  removeTag: async (conversationId: number, tagId: number) => {
    await api.delete(`/chat/conversations/${conversationId}/tags/${tagId}`)
  },
}
