import api from './api'
import { Template, TemplateCreate, TemplateUpdate, TemplateUsageRequest, Conversation, PaginationParams } from '../types'

export const templateService = {
  // Get all templates (user's private + public)
  getTemplates: async (params?: PaginationParams) => {
    const response = await api.get<Template[]>('/templates', { params })
    return response.data
  },

  // Get public templates only
  getPublicTemplates: async (params?: PaginationParams) => {
    const response = await api.get<Template[]>('/templates/public', { params })
    return response.data
  },

  // Get template by ID
  getTemplate: async (id: number) => {
    const response = await api.get<Template>(`/templates/${id}`)
    return response.data
  },

  // Create template
  createTemplate: async (data: TemplateCreate) => {
    const response = await api.post<Template>('/templates', data)
    return response.data
  },

  // Update template
  updateTemplate: async (id: number, data: TemplateUpdate) => {
    const response = await api.put<Template>(`/templates/${id}`, data)
    return response.data
  },

  // Delete template
  deleteTemplate: async (id: number) => {
    await api.delete(`/templates/${id}`)
  },

  // Use template to create conversation
  useTemplate: async (id: number, data: TemplateUsageRequest) => {
    const response = await api.post<Conversation>(`/templates/${id}/use`, data)
    return response.data
  },
}
