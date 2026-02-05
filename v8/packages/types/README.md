# @stock-debate/types

Shared TypeScript types and interfaces for the Stock Debate Advisor application.

## Installation

This package is part of the monorepo and uses workspace references:

```json
{
  "dependencies": {
    "@stock-debate/types": "workspace:*"
  }
}
```

## Usage

```typescript
import { Debate, DebateStatus, Timeframe, CreateDebateRequest } from '@stock-debate/types'

// Use the types in your application
const debate: Debate = {
  id: '123',
  userId: 'user-1',
  symbol: 'AAPL',
  timeframe: Timeframe.ONE_MONTH,
  status: DebateStatus.PENDING,
  verdict: null,
  confidence: null,
  reasoning: null,
  transcript: null,
  createdAt: new Date().toISOString(),
  updatedAt: null,
  completedAt: null,
}
```

## Exports

### Enums
- `DebateStatus` - Status of a debate (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- `DebateVerdict` - Verdict of a debate (BUY, HOLD, SELL)
- `DebateConfidence` - Confidence level (LOW, MEDIUM, HIGH)
- `Timeframe` - Investment timeframe (ONE_MONTH, THREE_MONTHS, SIX_MONTHS, ONE_YEAR)

### Models
- `Debate` - Core debate data structure
- `DebateReasoning` - Analysis reasoning
- `DebateTranscript` - Full debate transcript
- `DebateRound` - Single round of debate
- `Stock` - Stock information
- `User` - User profile

### API Types
- `CreateDebateRequest` - Request to create a debate
- `LoginRequest` - Authentication request
- `DebateListResponse` - List of debates response
- `ApiErrorResponse` - Error response format
- `HealthCheckResponse` - Health check response

## Scripts

- `pnpm type-check` - Run TypeScript type checking
