const STORAGE_PREFIX = 'llm_manager_'

export const storage = {
  set: (key: string, value: any): void => {
    try {
      const serialized = JSON.stringify(value)
      localStorage.setItem(STORAGE_PREFIX + key, serialized)
    } catch (error) {
      console.error('Storage set error:', error)
    }
  },

  get: <T = any>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(STORAGE_PREFIX + key)
      if (item === null) return defaultValue || null
      return JSON.parse(item) as T
    } catch (error) {
      console.error('Storage get error:', error)
      return defaultValue || null
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(STORAGE_PREFIX + key)
    } catch (error) {
      console.error('Storage remove error:', error)
    }
  },

  clear: (): void => {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith(STORAGE_PREFIX)) {
          localStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.error('Storage clear error:', error)
    }
  },
}
