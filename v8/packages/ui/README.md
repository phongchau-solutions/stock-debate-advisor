# @stock-debate/ui

Reusable React components and hooks for the Stock Debate Advisor application.

## Installation

This package is part of the monorepo and uses workspace references:

```json
{
  "dependencies": {
    "@stock-debate/ui": "workspace:*"
  }
}
```

## Usage

### Components

```typescript
import { DebateCard, LoadingSpinner, ErrorAlert } from '@stock-debate/ui'

// Use DebateCard
<DebateCard debate={debate} onClick={() => navigate(`/debates/${debate.id}`)} />

// Use LoadingSpinner
<LoadingSpinner message="Loading debates..." />

// Use ErrorAlert
<ErrorAlert error="Failed to load data" title="Loading Error" />
```

### Hooks

```typescript
import { useDebounce } from '@stock-debate/ui/hooks'

const [searchTerm, setSearchTerm] = useState('')
const debouncedSearchTerm = useDebounce(searchTerm, 500)

useEffect(() => {
  // This will only run 500ms after the user stops typing
  fetchResults(debouncedSearchTerm)
}, [debouncedSearchTerm])
```

## Components

### DebateCard
A card component for displaying debate information.

**Props:**
- `debate: Debate` - The debate object to display
- `onClick?: () => void` - Optional click handler

### LoadingSpinner
A centered loading spinner with optional message.

**Props:**
- `message?: string` - Optional loading message (default: "Loading...")

### ErrorAlert
An alert component for displaying errors.

**Props:**
- `error: string | Error` - The error to display
- `title?: string` - Optional error title (default: "Error")

## Hooks

### useDebounce
A hook to debounce a value.

**Parameters:**
- `value: T` - The value to debounce
- `delay?: number` - Debounce delay in milliseconds (default: 500)

**Returns:** `T` - The debounced value

## Scripts

- `pnpm type-check` - Run TypeScript type checking

## Dependencies

- Material UI 5.15+ (peer dependency)
- Font Awesome 6.5+
- React 18.3+ (peer dependency)
- @stock-debate/types (workspace)
