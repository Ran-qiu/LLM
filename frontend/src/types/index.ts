// ==========================================
// User Types
// ==========================================

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface UserRegister {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface UserUpdate {
  email?: string
  full_name?: string
  password?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  refresh_token?: string
}

// ==========================================
// API Key Types
// ==========================================

export interface APIKey {
  id: number
  user_id: number
  provider: string
  name: string
  is_active: boolean
  rpm_limit: number
  custom_config?: Record<string, any>
  last_used_at?: string
  created_at: string
  updated_at: string
}

export interface APIKeyCreate {
  provider: string
  name: string
  api_key: string
  base_url?: string
  model_name?: string
  rpm_limit?: number
  custom_config?: Record<string, any>
}

export interface APIKeyUpdate {
  name?: string
  api_key?: string
  base_url?: string
  model_name?: string
  is_active?: boolean
  rpm_limit?: number
  custom_config?: Record<string, any>
}

// ==========================================
// Conversation Types
// ==========================================

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  prompt_tokens?: number
  completion_tokens?: number
  total_tokens?: number
  cost?: number
  created_at: string
}

export interface Tag {
  id: number
  user_id: number
  name: string
  color?: string
  created_at: string
  updated_at: string
}

export interface Conversation {
  id: number
  user_id: number
  api_key_id: number
  title: string
  model: string
  system_prompt?: string
  created_at: string
  updated_at: string
  tags: Tag[]
  message_count?: number
  last_message_content?: string
  total_tokens?: number
  total_cost?: number
}

export interface ConversationCreate {
  title: string
  model: string
  api_key_id: number
  system_prompt?: string
}

export interface ConversationUpdate {
  title?: string
  system_prompt?: string
}

export interface ChatMessage {
  message: string
}

export interface ChatResponse {
  message: Message
  conversation: Conversation
}

// ==========================================
// Tag Types
// ==========================================

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}

// ==========================================
// Statistics Types
// ==========================================

export interface Statistics {
  summary: {
    total_conversations: number
    total_messages: number
    total_tokens: number
    total_cost: number
    active_api_keys: number
  }
  by_provider?: Record<string, {
    conversations: number
    messages: number
    tokens: number
    cost: number
  }>
  by_model?: Record<string, {
    conversations: number
    messages: number
    tokens: number
    cost: number
  }>
  by_date?: Array<{
    date: string
    messages: number
    tokens: number
    cost: number
  }>
}

export interface ConversationStatistics {
  conversation_id: number
  title: string
  model: string
  total_messages: number
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  total_cost: number
  created_at: string
  updated_at: string
  first_message_at?: string
  last_message_at?: string
}

// ==========================================
// Search & Export Types
// ==========================================

export interface SearchResult {
  message: Message
  conversation: {
    id: number
    title: string
  }
}

export interface SearchParams {
  query: string
  conversation_id?: number
  skip?: number
  limit?: number
}

// ==========================================
// Common Types
// ==========================================

export interface PaginationParams {
  skip?: number
  limit?: number
}

export interface ErrorResponse {
  detail: string
}

export interface SuccessResponse {
  message: string
}

// ==========================================
// Model Types
// ==========================================

export interface AvailableModel {
  provider: string
  model: string
  display_name: string
}
