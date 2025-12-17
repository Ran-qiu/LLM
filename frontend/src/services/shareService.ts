import api from './api'
import { Share, ShareCreate, ShareUpdate, ShareAccessRequest, Conversation, Message, PaginationParams } from '../types'

export const shareService = {
  // Get all shares
  getShares: async (params?: PaginationParams) => {
    const response = await api.get<Share[]>('/shares', { params })
    return response.data
  },

  // Get share by ID
  getShare: async (id: number) => {
    const response = await api.get<Share>(`/shares/${id}`)
    return response.data
  },

  // Create share
  createShare: async (conversationId: number, data?: ShareCreate) => {
    const response = await api.post<Share>(`/shares/conversations/${conversationId}`, data || {})
    return response.data
  },

  // Update share
  updateShare: async (id: number, data: ShareUpdate) => {
    const response = await api.put<Share>(`/shares/${id}`, data)
    return response.data
  },

  // Delete share
  deleteShare: async (id: number) => {
    await api.delete(`/shares/${id}`)
  },

  // Public endpoints (no auth required)
  getShareInfo: async (token: string) => {
    const response = await api.get<{ title: string; requires_password: boolean }>(`/shares/${token}/info`)
    return response.data
  },

  // Access shared conversation
  accessShare: async (token: string, data?: ShareAccessRequest) => {
    const response = await api.post<{ conversation: Conversation; messages: Message[] }>(
      `/shares/${token}/access`,
      data || {}
    )
    return response.data
  },
}
