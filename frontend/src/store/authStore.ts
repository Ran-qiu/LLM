import { create } from 'zustand'
import { User, UserLogin, UserRegister, TokenResponse } from '../types'
import api from '../services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (credentials: UserLogin) => Promise<void>
  register: (userData: UserRegister) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (credentials: UserLogin) => {
    set({ isLoading: true, error: null })
    try {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await api.post<TokenResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)

      // Fetch user info
      const userResponse = await api.get<User>('/auth/me')
      set({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
        isAuthenticated: false,
      })
      throw error
    }
  },

  register: async (userData: UserRegister) => {
    set({ isLoading: true, error: null })
    try {
      await api.post('/auth/register', userData)

      // Auto login after registration
      await useAuthStore.getState().login({
        username: userData.username,
        password: userData.password,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    })
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get<User>('/auth/me')
      set({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch user',
        isLoading: false,
        isAuthenticated: false,
        user: null,
      })
      localStorage.removeItem('access_token')
    }
  },

  clearError: () => set({ error: null }),
}))
