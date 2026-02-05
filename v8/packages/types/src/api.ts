import { Debate, Stock, User } from './models'
import { Timeframe } from './enums'

// Request types
export interface CreateDebateRequest {
  symbol: string
  timeframe: Timeframe
}

export interface LoginRequest {
  email: string
  password: string
}

// Response types
export interface DebateListResponse {
  debates: Debate[]
  total: number
}

export interface ApiErrorResponse {
  detail: string
  status?: number
}

export interface HealthCheckResponse {
  status: string
  service: string
}
