# @stock-debate/eslint-config

Shared ESLint configuration for the Stock Debate Advisor application.

## Installation

This package is part of the monorepo and uses workspace references:

```json
{
  "devDependencies": {
    "@stock-debate/eslint-config": "workspace:*"
  }
}
```

## Usage

Create an `.eslintrc.js` file in your app:

```javascript
module.exports = {
  extends: ['@stock-debate/eslint-config'],
  // Add your custom rules here
}
```

Or in `.eslintrc.json`:

```json
{
  "extends": ["@stock-debate/eslint-config"]
}
```

## Features

- TypeScript support with `@typescript-eslint`
- React and React Hooks rules
- Recommended ESLint rules
- Custom rules for unused variables (ignores `_` prefix)
- Disables `react/react-in-jsx-scope` for React 17+ JSX transform
- Disables `react/prop-types` for TypeScript projects

## Included Plugins

- `@typescript-eslint/eslint-plugin` - TypeScript-specific linting rules
- `@typescript-eslint/parser` - TypeScript parser for ESLint
- `eslint-plugin-react` - React-specific linting rules
- `eslint-plugin-react-hooks` - React Hooks rules

## Custom Rules

- `@typescript-eslint/no-unused-vars`: Error with `argsIgnorePattern: '^_'`
- `@typescript-eslint/no-explicit-any`: Warning
- `react/react-in-jsx-scope`: Off
- `react/prop-types`: Off
