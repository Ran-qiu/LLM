import api from './api'
import { User, UserUpdate } from '../types'

export const userService = {
  // Update current user
  updateCurrentUser: async (data: UserUpdate) => {
    const response = await api.put<User>('/users/me', data)
    return response.data
  },

  // Delete current user
  deleteCurrentUser: async () => {
    await api.delete('/users/me')
  },
}
