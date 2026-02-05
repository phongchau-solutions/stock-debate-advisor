// Common TypeScript types and interfaces

export interface User {
  id: string
  email: string
  displayName?: string
  photoURL?: string
  createdAt?: Date
}

export interface Stock {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

export interface Debate {
  id: string
  stockSymbol: string
  title: string
  description: string
  createdBy: string
  createdAt: Date
  updatedAt: Date
  participants: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}
