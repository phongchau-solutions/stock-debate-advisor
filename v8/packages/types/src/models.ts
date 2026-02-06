// Debate Models
export enum DebateStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum Verdict {
  BUY = 'BUY',
  HOLD = 'HOLD',
  SELL = 'SELL',
}

export enum Confidence {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
}

export enum Timeframe {
  ONE_MONTH = '1_month',
  THREE_MONTHS = '3_months',
  SIX_MONTHS = '6_months',
  ONE_YEAR = '1_year',
}

export interface Debate {
  id: string
  userId: string
  symbol: string
  timeframe: Timeframe
  status: DebateStatus
  verdict?: Verdict
  confidence?: Confidence
  reasoning?: Record<string, any>
  transcript?: Record<string, any>
  createdAt: string
  updatedAt?: string
  completedAt?: string
}

// User Models
export interface User {
  id: string
  email: string
  displayName?: string
  photoUrl?: string
  createdAt: string
  updatedAt?: string
}

// Stock Data Models
export interface StockPrice {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

export interface CompanyInfo {
  symbol: string
  name: string
  sector: string
  industry: string
  marketCap: number
  employees?: number
  website?: string
  description?: string
}
