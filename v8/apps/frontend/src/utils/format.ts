import { format as dateFnsFormat, formatDistanceToNow } from 'date-fns'

/**
 * Format a date to a specific format
 */
export const formatDate = (date: Date | string | number, format = 'PPP'): string => {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date
  return dateFnsFormat(dateObj, format)
}

/**
 * Format a date as relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: Date | string | number): string => {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date
  return formatDistanceToNow(dateObj, { addSuffix: true })
}

/**
 * Format a number as currency
 */
export const formatCurrency = (value: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value)
}

/**
 * Format a percentage value
 */
export const formatPercentage = (value: number, decimals = 2): string => {
  return `${value.toFixed(decimals)}%`
}

/**
 * Format a large number with abbreviations (K, M, B)
 */
export const formatNumber = (value: number): string => {
  if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`
  return value.toString()
}
