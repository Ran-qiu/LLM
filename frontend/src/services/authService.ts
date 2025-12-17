import api from './api'
import { User, UserRegister, UserLogin, TokenResponse } from '../types'

export const authService = {
  // Register new user
  register: async (userData: UserRegister) => {
    const response = await api.post<User>('/auth/register', userData)
    return response.data
  },

  // Login
  login: async (credentials: UserLogin) => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // Change password
  changePassword: async (oldPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },

  // Refresh token
  refreshToken: async (refreshToken: string) => {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}
