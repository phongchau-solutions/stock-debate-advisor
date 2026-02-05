# Shared TypeScript Packages

Shared libraries and configurations for the frontend.

## Packages

### @stock-debate/ui
Shared UI components built with Material Design 3.

### @stock-debate/types
TypeScript type definitions shared across the frontend.

### @stock-debate/utils
Common utility functions.

### @stock-debate/eslint-config
Shared ESLint configuration.

### @stock-debate/tsconfig
Shared TypeScript configurations.

### @stock-debate/tailwind-config
Shared Tailwind CSS configuration.

## Development

```bash
# Build all packages
pnpm build

# Test packages
pnpm test

# Lint packages
pnpm lint
```

## Usage

In your app's `package.json`:

```json
{
  "dependencies": {
    "@stock-debate/ui": "workspace:*",
    "@stock-debate/types": "workspace:*",
    "@stock-debate/utils": "workspace:*"
  }
}
```

## Status

🚧 **In Development** - Structure created, implementation pending
