# Shared TypeScript Packages

This directory contains 5 shared TypeScript packages that provide reusable code across the Stock Debate Advisor monorepo.

## Package Overview

### 1. @stock-debate/types
**Location:** `packages/types/`  
**Purpose:** Shared TypeScript types and interfaces

**Exports:**
- Enums: `DebateStatus`, `DebateVerdict`, `DebateConfidence`, `Timeframe`
- Models: `Debate`, `DebateReasoning`, `DebateTranscript`, `DebateRound`, `Stock`, `User`
- API Types: `CreateDebateRequest`, `LoginRequest`, `DebateListResponse`, `ApiErrorResponse`, `HealthCheckResponse`

**Usage:**
```typescript
import { Debate, DebateStatus, Timeframe } from '@stock-debate/types'
```

---

### 2. @stock-debate/ui
**Location:** `packages/ui/`  
**Purpose:** Reusable React components and hooks

**Exports:**
- Components: `DebateCard`, `LoadingSpinner`, `ErrorAlert`
- Hooks: `useDebounce`

**Dependencies:**
- Material UI 5.15+
- Font Awesome 6.5+
- React 18.3+ (peer)
- @stock-debate/types

**Usage:**
```typescript
import { DebateCard, LoadingSpinner, useDebounce } from '@stock-debate/ui'
```

---

### 3. @stock-debate/utils
**Location:** `packages/utils/`  
**Purpose:** Utility functions for formatting, validation, and constants

**Exports:**
- Format: `formatCurrency`, `formatPercent`, `formatLargeNumber`, `formatDate`, `formatRelativeTime`, `formatRelativeDate`
- Validation: `isValidEmail`, `isValidStockSymbol`, `isStrongPassword`, `sanitizeString`
- Constants: `TIMEFRAME_LABELS`, `API_BASE_URL`, `ROUTES`

**Dependencies:**
- date-fns 3.3+
- @stock-debate/types

**Usage:**
```typescript
import { formatCurrency, isValidEmail, TIMEFRAME_LABELS } from '@stock-debate/utils'
```

---

### 4. @stock-debate/eslint-config
**Location:** `packages/config/eslint-config/`  
**Purpose:** Shared ESLint configuration

**Features:**
- TypeScript support
- React and React Hooks rules
- Custom rules for unused variables
- Recommended ESLint rules

**Usage:**
```javascript
// .eslintrc.js
module.exports = {
  extends: ['@stock-debate/eslint-config'],
}
```

---

### 5. @stock-debate/tsconfig
**Location:** `packages/config/tsconfig/`  
**Purpose:** Shared TypeScript configurations

**Configurations:**
- `base.json` - Base TypeScript config for non-React projects
- `react.json` - React-specific config (extends base)

**Usage:**
```json
// For React projects
{
  "extends": "@stock-debate/tsconfig/react.json"
}

// For non-React projects
{
  "extends": "@stock-debate/tsconfig/base.json"
}
```

---

## Dependency Graph

```
@stock-debate/types (no dependencies)
    ↓
    ├── @stock-debate/ui (depends on types)
    └── @stock-debate/utils (depends on types)

@stock-debate/eslint-config (standalone)
@stock-debate/tsconfig (standalone)
```

**No circular dependencies!** ✅

---

## Installation

All packages are private workspace packages using pnpm workspaces. To use them in your app:

```json
{
  "dependencies": {
    "@stock-debate/types": "workspace:*",
    "@stock-debate/ui": "workspace:*",
    "@stock-debate/utils": "workspace:*"
  },
  "devDependencies": {
    "@stock-debate/eslint-config": "workspace:*",
    "@stock-debate/tsconfig": "workspace:*"
  }
}
```

Then run:
```bash
pnpm install
```

---

## Development

### Type Checking

Run type checking on all packages:
```bash
pnpm type-check
```

Or for a specific package:
```bash
cd packages/types && pnpm type-check
```

### Building

These packages are designed to be used directly as source TypeScript files (with `allowImportingTsExtensions` and bundler tools like Vite). No build step is required.

---

## Package Scripts

Each package has the following scripts:

- `type-check` - Run TypeScript type checking without emitting files

---

## Adding a New Package

1. Create the package directory under `packages/` or `packages/config/`
2. Add a `package.json` with:
   - `name: "@stock-debate/package-name"`
   - `version: "8.0.0"`
   - `private: true`
   - `type: "module"`
3. Add a `tsconfig.json` extending the appropriate base config
4. Create your source files
5. Add a `README.md` documenting the package
6. Run `pnpm install` to update the lockfile
7. Run `pnpm type-check` to verify

---

## Best Practices

1. **Keep packages focused** - Each package should have a single, clear responsibility
2. **Avoid circular dependencies** - `types` should have no dependencies, others can depend on it
3. **Use workspace references** - Always use `workspace:*` for internal dependencies
4. **Document exports** - Keep README files up-to-date with all exports
5. **Type everything** - Use TypeScript strict mode and avoid `any`
6. **Test imports** - Verify that packages can be imported and used correctly

---

## Version History

- **8.0.0** (2026-02-05) - Initial release with 5 packages
  - Created @stock-debate/types
  - Created @stock-debate/ui
  - Created @stock-debate/utils
  - Created @stock-debate/eslint-config
  - Created @stock-debate/tsconfig
