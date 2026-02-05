import { Timeframe } from '@stock-debate/types'

export const TIMEFRAME_LABELS: Record<Timeframe, string> = {
  [Timeframe.ONE_MONTH]: '1 Month',
  [Timeframe.THREE_MONTHS]: '3 Months',
  [Timeframe.SIX_MONTHS]: '6 Months',
  [Timeframe.ONE_YEAR]: '1 Year',
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DEBATES: '/debates',
  DEBATE_DETAIL: '/debates/:id',
  CREATE_DEBATE: '/debates/new',
} as const
