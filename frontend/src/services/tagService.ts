import api from './api'
import { Tag, TagCreate, TagUpdate, Conversation, PaginationParams } from '../types'

export const tagService = {
  // Get all tags
  getTags: async (params?: PaginationParams) => {
    const response = await api.get<Tag[]>('/tags', { params })
    return response.data
  },

  // Get tag by ID
  getTag: async (id: number) => {
    const response = await api.get<Tag>(`/tags/${id}`)
    return response.data
  },

  // Create tag
  createTag: async (data: TagCreate) => {
    const response = await api.post<Tag>('/tags', data)
    return response.data
  },

  // Update tag
  updateTag: async (id: number, data: TagUpdate) => {
    const response = await api.put<Tag>(`/tags/${id}`, data)
    return response.data
  },

  // Delete tag
  deleteTag: async (id: number) => {
    await api.delete(`/tags/${id}`)
  },

  // Get conversations by tag
  getConversationsByTag: async (tagId: number, params?: PaginationParams) => {
    const response = await api.get<Conversation[]>(`/tags/${tagId}/conversations`, { params })
    return response.data
  },
}
