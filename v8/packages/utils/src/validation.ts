/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
  return emailRegex.test(email)
}

/**
 * Validate stock symbol (1-10 uppercase letters)
 */
export function isValidStockSymbol(symbol: string): boolean {
  const symbolRegex = /^[A-Z]{1,10}$/
  return symbolRegex.test(symbol)
}

/**
 * Validate password strength
 * Requires: at least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
 * Special characters allowed: !@#$%^&*(),.?":{}|<>
 */
export function isStrongPassword(password: string): boolean {
  if (password.length < 8) return false
  if (!/[A-Z]/.test(password)) return false
  if (!/[a-z]/.test(password)) return false
  if (!/[0-9]/.test(password)) return false
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return false
  return true
}

/**
 * Sanitize string for display (prevent XSS)
 */
export function sanitizeString(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}
