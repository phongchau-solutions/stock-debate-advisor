import { format, formatDistance, formatRelative } from 'date-fns'

/**
 * Format a number as currency (USD)
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Format a number as percentage
 * Note: value should be the percentage value (e.g., 5.5 for 5.5%), not a decimal (0.055)
 * @example
 * formatPercent(5.5) // returns "+5.50%"
 * formatPercent(-2.3) // returns "-2.30%"
 * formatPercent(10.123, 1) // returns "+10.1%"
 */
export function formatPercent(value: number, decimals: number = 2): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

/**
 * Format large numbers (e.g., 1.5M, 2.3B)
 */
export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(value)
}

/**
 * Format a date string
 */
export function formatDate(date: string | Date, formatStr: string = 'PP'): string {
  return format(new Date(date), formatStr)
}

/**
 * Format a date as relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  return formatDistance(new Date(date), new Date(), { addSuffix: true })
}

/**
 * Format a date as relative date (e.g., "today at 3:30 PM")
 */
export function formatRelativeDate(date: string | Date): string {
  return formatRelative(new Date(date), new Date())
}

/**
 * Format date with time
 */
export function formatDateTime(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy h:mm a')
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
