import api from './api'
import { APIKey, APIKeyCreate, APIKeyUpdate, PaginationParams } from '../types'

export const apiKeyService = {
  // Get all API keys
  getAPIKeys: async (params?: PaginationParams) => {
    const response = await api.get<APIKey[]>('/users/me/api-keys', { params })
    return response.data
  },

  // Get API key by ID
  getAPIKey: async (id: number) => {
    const response = await api.get<APIKey>(`/users/me/api-keys/${id}`)
    return response.data
  },

  // Create API key
  createAPIKey: async (data: APIKeyCreate) => {
    const response = await api.post<APIKey>('/users/me/api-keys', data)
    return response.data
  },

  // Update API key
  updateAPIKey: async (id: number, data: APIKeyUpdate) => {
    const response = await api.put<APIKey>(`/users/me/api-keys/${id}`, data)
    return response.data
  },

  // Delete API key
  deleteAPIKey: async (id: number) => {
    await api.delete(`/users/me/api-keys/${id}`)
  },

  // Get available models
  getAvailableModels: async () => {
    const response = await api.get('/models/available')
    return response.data
  },
}
