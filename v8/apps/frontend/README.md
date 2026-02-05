# Frontend Application

React 18 (LTS) + TypeScript + Vite application for Stock Debate Advisor.

## Features

- Real-time debate updates
- Stock search and analysis
- User authentication (Firebase)
- Material Design 3 UI
- Responsive design

## Development

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint
pnpm lint
```

## Technology Stack

- React 18.3 (LTS)
- TypeScript 5.3+
- Vite 5.0+
- Material Design 3
- Font Awesome 7
- Tailwind CSS
- TanStack Query
- Zustand

## Structure

```
src/
├── components/     # Reusable components
├── features/       # Feature modules
├── hooks/          # Custom hooks
├── services/       # API services
├── stores/         # State management
├── types/          # TypeScript types
├── utils/          # Utility functions
└── App.tsx         # Main app
```

## Environment Variables

Create `.env.local`:

```
VITE_FIREBASE_API_KEY=your-key
VITE_FIREBASE_PROJECT_ID=your-project
VITE_FIREBASE_AUTH_DOMAIN=your-domain
```

## Status

🚧 **In Development** - Structure created, implementation pending
