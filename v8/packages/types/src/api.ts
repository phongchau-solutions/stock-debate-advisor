import { Debate, DebateStatus, Timeframe, Verdict, Confidence } from './models'

// Request/Response Types

export interface CreateDebateRequest {
  symbol: string
  timeframe: Timeframe
}

export interface CreateDebateResponse extends Debate {}

export interface GetDebateResponse extends Debate {}

export interface ListDebatesResponse {
  debates: Debate[]
  total: number
}

export interface ApiError {
  detail: string
  status?: number
}

export interface PaginationParams {
  skip?: number
  limit?: number
}

// WebSocket Messages
export interface DebateUpdateMessage {
  type: 'debate_update'
  debateId: string
  status: DebateStatus
  progress?: number
  message?: string
}

export interface DebateCompletedMessage {
  type: 'debate_completed'
  debateId: string
  verdict: Verdict
  confidence: Confidence
  reasoning: Record<string, any>
}

export type WebSocketMessage = DebateUpdateMessage | DebateCompletedMessage
