import { DebateStatus, DebateVerdict, DebateConfidence, Timeframe } from './enums.ts'

export interface Debate {
  id: string
  userId: string
  symbol: string
  timeframe: Timeframe
  status: DebateStatus
  verdict: DebateVerdict | null
  confidence: DebateConfidence | null
  reasoning: DebateReasoning | null
  transcript: DebateTranscript | null
  createdAt: string
  updatedAt: string | null
  completedAt: string | null
}

export interface DebateReasoning {
  fundamental: string
  technical: string
  sentiment: string
  summary: string
}

export interface DebateTranscript {
  rounds: DebateRound[]
  finalVerdict: string
}

export interface DebateRound {
  round: number
  fundamentalAnalyst: string
  technicalAnalyst: string
  sentimentAnalyst: string
  judge: string
}

export interface Stock {
  symbol: string
  name: string
  sector: string
  industry: string
  marketCap: number
  price: number
  change: number
  changePercent: number
}

export interface User {
  id: string
  email: string
  displayName: string | null
  photoUrl: string | null
  createdAt: string
}
