# @stock-debate/utils

Utility functions for the Stock Debate Advisor application.

## Installation

This package is part of the monorepo and uses workspace references:

```json
{
  "dependencies": {
    "@stock-debate/utils": "workspace:*"
  }
}
```

## Usage

### Formatting

```typescript
import { 
  formatCurrency, 
  formatPercent, 
  formatLargeNumber,
  formatDate,
  formatRelativeTime,
  formatRelativeDate
} from '@stock-debate/utils'

formatCurrency(1234.56) // "$1,234.56"
formatPercent(0.0525) // "5.25%"
formatLargeNumber(1500000) // "1.50M"
formatDate(new Date()) // "Feb 5, 2026"
formatRelativeTime(new Date()) // "2 hours ago"
formatRelativeDate(new Date()) // "today at 3:30 PM"
```

### Validation

```typescript
import { 
  isValidEmail, 
  isValidStockSymbol, 
  isStrongPassword,
  sanitizeString
} from '@stock-debate/utils'

isValidEmail('user@example.com') // true
isValidStockSymbol('AAPL') // true
isStrongPassword('SecurePass123') // true
sanitizeString('<script>alert("xss")</script>') // "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
```

### Constants

```typescript
import { TIMEFRAME_LABELS, API_BASE_URL, ROUTES } from '@stock-debate/utils'

console.log(TIMEFRAME_LABELS[Timeframe.ONE_MONTH]) // "1 Month"
console.log(API_BASE_URL) // "http://localhost:8000"
console.log(ROUTES.DEBATES) // "/debates"
```

## Functions

### Formatting

- `formatCurrency(value: number): string` - Format number as USD currency
- `formatPercent(value: number, decimals?: number): string` - Format number as percentage
- `formatLargeNumber(value: number): string` - Format with K, M, B, T abbreviations
- `formatDate(date: string | Date, formatStr?: string): string` - Format date using date-fns
- `formatRelativeTime(date: string | Date): string` - Format as relative time (e.g., "2 hours ago")
- `formatRelativeDate(date: string | Date): string` - Format as relative date (e.g., "today at 3:30 PM")

### Validation

- `isValidEmail(email: string): boolean` - Validate email format
- `isValidStockSymbol(symbol: string): boolean` - Validate stock symbol (1-10 uppercase letters)
- `isStrongPassword(password: string): boolean` - Validate password strength (8+ chars, 1 upper, 1 lower, 1 number)
- `sanitizeString(str: string): string` - Sanitize string to prevent XSS attacks

### Constants

- `TIMEFRAME_LABELS` - Human-readable labels for Timeframe enum values
- `API_BASE_URL` - Base URL for API requests
- `ROUTES` - Application route paths

## Scripts

- `pnpm type-check` - Run TypeScript type checking

## Dependencies

- date-fns 3.3+
- @stock-debate/types (workspace)
