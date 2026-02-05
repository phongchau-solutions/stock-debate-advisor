# @stock-debate/tsconfig

Shared TypeScript configurations for the Stock Debate Advisor application.

## Installation

This package is part of the monorepo and uses workspace references:

```json
{
  "devDependencies": {
    "@stock-debate/tsconfig": "workspace:*"
  }
}
```

## Usage

### For Base TypeScript Projects

Create a `tsconfig.json` file in your app:

```json
{
  "extends": "@stock-debate/tsconfig/base.json",
  "compilerOptions": {
    // Add your custom options here
  },
  "include": ["src/**/*"]
}
```

### For React Projects

Create a `tsconfig.json` file in your app:

```json
{
  "extends": "@stock-debate/tsconfig/react.json",
  "compilerOptions": {
    // Add your custom options here
  },
  "include": ["src/**/*"]
}
```

## Configurations

### base.json

Base TypeScript configuration for non-React projects:

- Target: ES2020
- Module: ESNext with bundler resolution
- Strict mode enabled
- Unused locals and parameters checking
- No fallthrough cases in switch statements
- ES module interop
- Consistent casing in file names

### react.json

Extends `base.json` with React-specific settings:

- DOM and DOM.Iterable libraries
- JSX: react-jsx (React 17+ transform)
- No emit (for build tools like Vite)

## Features

- Strict type checking
- Modern ES2020 target
- Bundler module resolution
- JSON module support
- TypeScript extensions allowed for imports
- Isolated modules for better performance
- Skip lib checks for faster compilation
- Enforce unused variable detection
