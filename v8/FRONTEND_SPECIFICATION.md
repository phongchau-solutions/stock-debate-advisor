# Stock Debate Advisor v8 - Frontend Specification

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026

---

## Frontend Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3+ | UI framework |
| **TypeScript** | 5.3+ | Type safety |
| **Vite** | 5.0+ | Build tool & dev server |
| **Tailwind CSS** | 3.4+ | Utility-first CSS |
| **Font Awesome** | 7.0+ (Free) | Icon library |
| **Material Design 3** | Latest | Design system & components |

### Additional Libraries

| Library | Purpose |
|---------|---------|
| **@mui/material** | Material Design 3 components |
| **@mui/material-nextgen** | Material Design 3 (M3) support |
| **@fortawesome/react-fontawesome** | Font Awesome React components |
| **@fortawesome/free-solid-svg-icons** | FA solid icons |
| **@fortawesome/free-regular-svg-icons** | FA regular icons |
| **@fortawesome/free-brands-svg-icons** | FA brand icons |
| **Firebase SDK** | Backend integration |
| **TanStack Query (React Query)** | Server state management |
| **Zustand** | Client state management |
| **React Router** | Routing |
| **Recharts** | Data visualization |
| **date-fns** | Date utilities |

---

## Project Setup

### Installation

```bash
# Create new Vite + React + TypeScript project
npm create vite@latest stock-debate-frontend -- --template react-ts

cd stock-debate-frontend

# Install core dependencies
npm install

# Install Material Design 3
npm install @mui/material @mui/material-nextgen @emotion/react @emotion/styled

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Font Awesome v7
npm install @fortawesome/fontawesome-svg-core
npm install @fortawesome/free-solid-svg-icons
npm install @fortawesome/free-regular-svg-icons
npm install @fortawesome/free-brands-svg-icons
npm install @fortawesome/react-fontawesome

# Install Firebase
npm install firebase

# Install state management & data fetching
npm install @tanstack/react-query zustand

# Install routing
npm install react-router-dom

# Install utilities
npm install recharts date-fns axios

# Install dev dependencies
npm install -D @types/node
```

### Configuration Files

#### `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Material Design 3 color tokens
        primary: {
          DEFAULT: '#6750A4',
          50: '#F4ECFF',
          100: '#E8DAFF',
          200: '#D0BCFF',
          300: '#B69DFF',
          400: '#9D7FFF',
          500: '#6750A4',
          600: '#4F378B',
          700: '#381E72',
          800: '#22005D',
          900: '#1A0048',
        },
        secondary: {
          DEFAULT: '#625B71',
          50: '#F7F2FA',
          100: '#E8DEF8',
          200: '#CCC2DC',
          300: '#B0A7C0',
          400: '#958DA5',
          500: '#625B71',
          600: '#4A4458',
          700: '#332D41',
          800: '#1D192B',
          900: '#120D1F',
        },
        tertiary: {
          DEFAULT: '#7D5260',
          50: '#FFEDF0',
          100: '#FFDAE0',
          200: '#FFB1C8',
          300: '#FF89AA',
          400: '#EFB8C8',
          500: '#7D5260',
          600: '#633B48',
          700: '#492532',
          800: '#31111D',
          900: '#1F0510',
        },
        error: {
          DEFAULT: '#BA1A1A',
          50: '#FFEDEA',
          100: '#FFDAD6',
          200: '#FFB4AB',
          300: '#FF897D',
          400: '#FF5449',
          500: '#BA1A1A',
          600: '#93000A',
          700: '#690005',
          800: '#410002',
          900: '#2D0001',
        },
        success: {
          DEFAULT: '#2E7D32',
          light: '#60AD5E',
          dark: '#005005',
        },
        warning: {
          DEFAULT: '#F57C00',
          light: '#FFB74D',
          dark: '#E65100',
        },
        // Surface colors
        surface: {
          DEFAULT: '#FFFBFE',
          variant: '#E7E0EC',
          dim: '#DED8E1',
          bright: '#FFF8FF',
          container: {
            DEFAULT: '#F3EDF7',
            low: '#F7F2FA',
            high: '#ECE6F0',
            highest: '#E6E0E9',
          }
        },
        // On colors (text on surfaces)
        'on-primary': '#FFFFFF',
        'on-secondary': '#FFFFFF',
        'on-tertiary': '#FFFFFF',
        'on-surface': '#1C1B1F',
        'on-surface-variant': '#49454F',
        'on-error': '#FFFFFF',
        // Outline
        outline: {
          DEFAULT: '#79747E',
          variant: '#CAC4D0',
        },
      },
      borderRadius: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '28px',
        'full': '9999px',
      },
      boxShadow: {
        'elevation-1': '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
        'elevation-2': '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)',
        'elevation-3': '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px rgba(0, 0, 0, 0.3)',
        'elevation-4': '0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 2px 3px rgba(0, 0, 0, 0.3)',
        'elevation-5': '0px 8px 12px 6px rgba(0, 0, 0, 0.15), 0px 4px 4px rgba(0, 0, 0, 0.3)',
      },
      fontFamily: {
        sans: ['Roboto', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Google Sans', 'Roboto', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      fontSize: {
        'display-large': ['57px', { lineHeight: '64px', fontWeight: '400' }],
        'display-medium': ['45px', { lineHeight: '52px', fontWeight: '400' }],
        'display-small': ['36px', { lineHeight: '44px', fontWeight: '400' }],
        'headline-large': ['32px', { lineHeight: '40px', fontWeight: '400' }],
        'headline-medium': ['28px', { lineHeight: '36px', fontWeight: '400' }],
        'headline-small': ['24px', { lineHeight: '32px', fontWeight: '400' }],
        'title-large': ['22px', { lineHeight: '28px', fontWeight: '500' }],
        'title-medium': ['16px', { lineHeight: '24px', fontWeight: '500' }],
        'title-small': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'body-large': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-medium': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'body-small': ['12px', { lineHeight: '16px', fontWeight: '400' }],
        'label-large': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'label-medium': ['12px', { lineHeight: '16px', fontWeight: '500' }],
        'label-small': ['11px', { lineHeight: '16px', fontWeight: '500' }],
      },
    },
  },
  plugins: [],
}
```

#### `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@features': path.resolve(__dirname, './src/features'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'firebase-vendor': ['firebase/app', 'firebase/auth', 'firebase/firestore'],
          'ui-vendor': ['@mui/material', '@mui/material-nextgen'],
          'icons-vendor': ['@fortawesome/react-fontawesome', '@fortawesome/free-solid-svg-icons'],
        },
      },
    },
  },
})
```

#### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@features/*": ["./src/features/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@services/*": ["./src/services/*"],
      "@store/*": ["./src/store/*"],
      "@utils/*": ["./src/utils/*"],
      "@types/*": ["./src/types/*"],
      "@assets/*": ["./src/assets/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── manifest.json
│   └── robots.txt
│
├── src/
│   ├── assets/                    # Static assets
│   │   ├── images/
│   │   └── fonts/
│   │
│   ├── components/                # Reusable components
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.module.css
│   │   │   │   └── index.ts
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   ├── Badge/
│   │   │   └── Spinner/
│   │   │
│   │   ├── layout/
│   │   │   ├── AppBar/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── Container/
│   │   │
│   │   ├── debate/
│   │   │   ├── DebateCard/
│   │   │   ├── DebateStatus/
│   │   │   ├── VerdictDisplay/
│   │   │   └── DebateProgress/
│   │   │
│   │   └── analytics/
│   │       ├── StockChart/
│   │       ├── PriceChart/
│   │       ├── TrendIndicator/
│   │       └── SentimentGauge/
│   │
│   ├── features/                  # Feature modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── SignupForm.tsx
│   │   │   │   └── AuthGuard.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts
│   │   │   │   └── useAuthState.ts
│   │   │   ├── services/
│   │   │   │   └── authService.ts
│   │   │   └── types/
│   │   │       └── auth.types.ts
│   │   │
│   │   ├── debates/
│   │   │   ├── components/
│   │   │   │   ├── DebateList.tsx
│   │   │   │   ├── DebateDetail.tsx
│   │   │   │   ├── CreateDebate.tsx
│   │   │   │   └── DebateHistory.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useDebates.ts
│   │   │   │   ├── useCreateDebate.ts
│   │   │   │   └── useDebateStream.ts
│   │   │   ├── services/
│   │   │   │   └── debateService.ts
│   │   │   └── types/
│   │   │       └── debate.types.ts
│   │   │
│   │   ├── stocks/
│   │   │   ├── components/
│   │   │   │   ├── StockSearch.tsx
│   │   │   │   ├── StockCard.tsx
│   │   │   │   ├── StockDetails.tsx
│   │   │   │   └── Watchlist.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useStockData.ts
│   │   │   │   └── useStockPrices.ts
│   │   │   ├── services/
│   │   │   │   └── stockService.ts
│   │   │   └── types/
│   │   │       └── stock.types.ts
│   │   │
│   │   ├── analytics/
│   │   │   ├── components/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── TrendAnalysis.tsx
│   │   │   │   └── PerformanceMetrics.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAnalytics.ts
│   │   │   └── services/
│   │   │       └── analyticsService.ts
│   │   │
│   │   └── settings/
│   │       ├── components/
│   │       │   ├── Profile.tsx
│   │       │   ├── Preferences.tsx
│   │       │   └── Notifications.tsx
│   │       └── hooks/
│   │           └── useSettings.ts
│   │
│   ├── hooks/                     # Global custom hooks
│   │   ├── useFirebase.ts
│   │   ├── useRealtime.ts
│   │   ├── useNotification.ts
│   │   └── useDebounce.ts
│   │
│   ├── services/                  # API services
│   │   ├── firebase/
│   │   │   ├── config.ts
│   │   │   ├── auth.ts
│   │   │   ├── firestore.ts
│   │   │   └── functions.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── websocket/
│   │       └── debateStream.ts
│   │
│   ├── store/                     # State management
│   │   ├── authStore.ts
│   │   ├── debateStore.ts
│   │   ├── uiStore.ts
│   │   └── index.ts
│   │
│   ├── types/                     # TypeScript types
│   │   ├── index.ts
│   │   ├── api.types.ts
│   │   ├── common.types.ts
│   │   └── firebase.types.ts
│   │
│   ├── utils/                     # Utility functions
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   │
│   ├── styles/                    # Global styles
│   │   ├── index.css
│   │   ├── tailwind.css
│   │   └── material-theme.ts
│   │
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   └── vite-env.d.ts             # Vite types
│
├── .env.example
├── .env.development
├── .env.production
├── .gitignore
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## Component Examples

### Material 3 Theme Configuration

```typescript
// src/styles/material-theme.ts

import { createTheme } from '@mui/material/styles';

export const materialTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6750A4',
      light: '#D0BCFF',
      dark: '#381E72',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#625B71',
      light: '#E8DEF8',
      dark: '#332D41',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#BA1A1A',
      light: '#FFDAD6',
      dark: '#410002',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FFFBFE',
      paper: '#F3EDF7',
    },
    text: {
      primary: '#1C1B1F',
      secondary: '#49454F',
    },
  },
  shape: {
    borderRadius: 12,
  },
  typography: {
    fontFamily: 'Roboto, Inter, system-ui, sans-serif',
    displayLarge: {
      fontSize: '57px',
      lineHeight: '64px',
      fontWeight: 400,
    },
    headlineLarge: {
      fontSize: '32px',
      lineHeight: '40px',
      fontWeight: 400,
    },
    titleLarge: {
      fontSize: '22px',
      lineHeight: '28px',
      fontWeight: 500,
    },
    bodyLarge: {
      fontSize: '16px',
      lineHeight: '24px',
      fontWeight: 400,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '20px',
          textTransform: 'none',
          fontSize: '14px',
          fontWeight: 500,
          padding: '10px 24px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '4px',
          },
        },
      },
    },
  },
});
```

### Button Component with Font Awesome

```typescript
// src/components/common/Button/Button.tsx

import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';

interface ButtonProps extends Omit<MuiButtonProps, 'startIcon' | 'endIcon'> {
  icon?: IconDefinition;
  iconPosition?: 'start' | 'end';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  icon,
  iconPosition = 'start',
  loading = false,
  disabled,
  ...props
}) => {
  const renderIcon = () => {
    if (loading) {
      return <FontAwesomeIcon icon="spinner" spin />;
    }
    if (icon) {
      return <FontAwesomeIcon icon={icon} />;
    }
    return null;
  };

  const iconElement = renderIcon();

  return (
    <MuiButton
      {...props}
      disabled={disabled || loading}
      startIcon={iconPosition === 'start' ? iconElement : undefined}
      endIcon={iconPosition === 'end' ? iconElement : undefined}
    >
      {children}
    </MuiButton>
  );
};
```

### Debate Card Component

```typescript
// src/features/debates/components/DebateCard.tsx

import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChartLine,
  faClock,
  faCheckCircle,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons';
import { Debate, DebateStatus } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface DebateCardProps {
  debate: Debate;
  onClick?: () => void;
}

export const DebateCard: React.FC<DebateCardProps> = ({ debate, onClick }) => {
  const getStatusIcon = (status: DebateStatus) => {
    switch (status) {
      case 'COMPLETED':
        return faCheckCircle;
      case 'IN_PROGRESS':
        return faSpinner;
      default:
        return faClock;
    }
  };

  const getStatusColor = (status: DebateStatus) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'IN_PROGRESS':
        return 'info';
      case 'FAILED':
        return 'error';
      default:
        return 'default';
    }
  };

  const getVerdictColor = (recommendation: string) => {
    switch (recommendation) {
      case 'BUY':
        return 'text-success';
      case 'SELL':
        return 'text-error';
      default:
        return 'text-warning';
    }
  };

  return (
    <Card
      className="hover:shadow-elevation-3 transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <CardContent>
        <Box className="flex items-start justify-between mb-4">
          <Box className="flex items-center gap-2">
            <FontAwesomeIcon icon={faChartLine} className="text-primary" size="lg" />
            <Typography variant="h6" className="font-semibold">
              {debate.symbol}
            </Typography>
          </Box>
          <Chip
            icon={<FontAwesomeIcon icon={getStatusIcon(debate.status)} />}
            label={debate.status}
            color={getStatusColor(debate.status)}
            size="small"
          />
        </Box>

        {debate.verdict && (
          <Box className="mb-3">
            <Typography variant="body2" color="text.secondary" className="mb-1">
              Verdict
            </Typography>
            <Typography
              variant="h5"
              className={`font-bold ${getVerdictColor(debate.verdict.recommendation)}`}
            >
              {debate.verdict.recommendation}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Confidence: {(debate.verdict.confidence * 100).toFixed(0)}%
            </Typography>
          </Box>
        )}

        <Box className="flex items-center gap-4 text-sm text-on-surface-variant">
          <Box className="flex items-center gap-1">
            <FontAwesomeIcon icon={faClock} />
            <span>{formatDistanceToNow(new Date(debate.createdAt), { addSuffix: true })}</span>
          </Box>
          <span>•</span>
          <span>{debate.rounds} rounds</span>
        </Box>
      </CardContent>
    </Card>
  );
};
```

### Stock Search Component

```typescript
// src/features/stocks/components/StockSearch.tsx

import React, { useState, useCallback } from 'react';
import { TextField, Autocomplete, CircularProgress, Box, Typography } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faBuildingColumns } from '@fortawesome/free-solid-svg-icons';
import { useDebounce } from '@/hooks/useDebounce';
import { searchStocks } from '@/services/api/stockService';

interface Stock {
  symbol: string;
  name: string;
  exchange: string;
}

interface StockSearchProps {
  onSelect: (stock: Stock) => void;
}

export const StockSearch: React.FC<StockSearchProps> = ({ onSelect }) => {
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  
  const debouncedSearch = useDebounce(inputValue, 300);

  React.useEffect(() => {
    if (debouncedSearch.length < 2) {
      setOptions([]);
      return;
    }

    setLoading(true);
    searchStocks(debouncedSearch)
      .then((results) => setOptions(results))
      .catch((error) => console.error('Search failed:', error))
      .finally(() => setLoading(false));
  }, [debouncedSearch]);

  return (
    <Autocomplete
      options={options}
      loading={loading}
      inputValue={inputValue}
      onInputChange={(_, value) => setInputValue(value)}
      onChange={(_, value) => value && onSelect(value)}
      getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Search stocks"
          placeholder="Enter symbol or company name"
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <Box className="ml-2">
                <FontAwesomeIcon icon={faSearch} className="text-on-surface-variant" />
              </Box>
            ),
            endAdornment: (
              <>
                {loading && <CircularProgress size={20} />}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <li {...props}>
          <Box className="flex items-center gap-3 py-2">
            <FontAwesomeIcon
              icon={faBuildingColumns}
              className="text-primary"
              size="lg"
            />
            <Box>
              <Typography variant="body1" className="font-medium">
                {option.symbol}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {option.name}
              </Typography>
            </Box>
          </Box>
        </li>
      )}
      noOptionsText={
        inputValue.length < 2
          ? 'Type at least 2 characters'
          : 'No stocks found'
      }
    />
  );
};
```

---

## Font Awesome Setup

### Initialize Font Awesome

```typescript
// src/utils/fontawesome.ts

import { library } from '@fortawesome/fontawesome-svg-core';

// Import solid icons
import {
  faHome,
  faChartLine,
  faUser,
  faCog,
  faBell,
  faSearch,
  faPlus,
  faEdit,
  faTrash,
  faCheckCircle,
  faExclamationCircle,
  faSpinner,
  faClock,
  faArrowUp,
  faArrowDown,
  faBuildingColumns,
  faNewspaper,
  faComments,
  faLightbulb,
  faChartBar,
  faFilter,
  faDownload,
  faShare,
  faStar,
  faHeart,
  faBookmark,
  faSignOut,
  faSignIn,
  faEye,
  faEyeSlash,
} from '@fortawesome/free-solid-svg-icons';

// Import regular icons
import {
  faStar as farStar,
  faHeart as farHeart,
  faBookmark as farBookmark,
} from '@fortawesome/free-regular-svg-icons';

// Import brand icons
import {
  faGoogle,
  faGithub,
  faTwitter,
  faLinkedin,
} from '@fortawesome/free-brands-svg-icons';

// Add icons to library
library.add(
  // Solid icons
  faHome,
  faChartLine,
  faUser,
  faCog,
  faBell,
  faSearch,
  faPlus,
  faEdit,
  faTrash,
  faCheckCircle,
  faExclamationCircle,
  faSpinner,
  faClock,
  faArrowUp,
  faArrowDown,
  faBuildingColumns,
  faNewspaper,
  faComments,
  faLightbulb,
  faChartBar,
  faFilter,
  faDownload,
  faShare,
  faStar,
  faHeart,
  faBookmark,
  faSignOut,
  faSignIn,
  faEye,
  faEyeSlash,
  // Regular icons
  farStar,
  farHeart,
  farBookmark,
  // Brand icons
  faGoogle,
  faGithub,
  faTwitter,
  faLinkedin
);
```

### Use in Main Entry

```typescript
// src/main.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import { materialTheme } from './styles/material-theme';
import './styles/index.css';
import './utils/fontawesome'; // Initialize Font Awesome

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={materialTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

---

## Firebase Integration

### Firebase Configuration

```typescript
// src/services/firebase/config.ts

import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getFunctions } from 'firebase/functions';
import { getStorage } from 'firebase/storage';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const functions = getFunctions(app);
export const storage = getStorage(app);
export const realtimeDb = getDatabase(app);

export default app;
```

### Environment Variables

```bash
# .env.development

VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
VITE_FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

---

## State Management with Zustand

```typescript
// src/store/authStore.ts

import { create } from 'zustand';
import { User } from 'firebase/auth';

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  error: null,
  setUser: (user) => set({ user, loading: false }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  logout: () => set({ user: null, loading: false, error: null }),
}));
```

---

## Package.json Scripts

```json
{
  "name": "stock-debate-frontend",
  "version": "8.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "test": "vitest",
    "deploy": "npm run build && firebase deploy --only hosting"
  }
}
```

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Ready for Implementation
