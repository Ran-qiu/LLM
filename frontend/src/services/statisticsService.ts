import api from './api'
import { Statistics, ConversationStatistics } from '../types'

export const statisticsService = {
  // Get user statistics
  getUserStatistics: async (days: number = 30) => {
    const response = await api.get<Statistics>('/statistics/me', {
      params: { days },
    })
    return response.data
  },

  // Get conversation statistics
  getConversationStatistics: async (conversationId: number) => {
    const response = await api.get<ConversationStatistics>(`/statistics/conversations/${conversationId}`)
    return response.data
  },
}
