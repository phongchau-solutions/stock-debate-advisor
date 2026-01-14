# Stock Debate Advisor - Backend Service

Node.js Express backend service that acts as a bridge between the frontend, data-service, and ai-service.

## Overview

The backend service provides:
- **API Gateway**: Single entry point for frontend with rate limiting and request validation
- **Service Bridge**: Proxies requests to data-service and ai-service with error handling
- **Session Management**: Manages debate sessions and user state
- **Request Aggregation**: Combines data from multiple services for frontend consumption
- **Authentication**: Token-based auth (JWT) for API endpoints
- **Error Handling**: Comprehensive error handling and logging

## Architecture

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────────────────────┐
│    Backend Service          │
│  (Express.js - Port 8000)   │
│                             │
│  ├─ API Routes              │
│  ├─ Middleware              │
│  ├─ Error Handling          │
│  └─ Logging                 │
└──────┬─────────────┬────────┘
       │             │
       │ HTTP/REST   │ HTTP/REST
       │             │
┌──────▼────┐   ┌────▼──────────┐
│ Data      │   │ AI Service    │
│ Service   │   │ (Port 8003)   │
│ (Port 8001)  │               │
└───────────┘   └───────────────┘
```

## Installation

```bash
npm install
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Server Configuration
NODE_ENV=development
PORT=8000
HOST=0.0.0.0

# Service URLs
DATA_SERVICE_URL=http://data-service:8001
AI_SERVICE_URL=http://ai-service:8003

# Logging
LOG_LEVEL=debug

# API Configuration
API_TIMEOUT=30000
ENABLE_CORS=true
CORS_ORIGIN=*

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

## Running the Service

### Development

```bash
npm run dev
```

### Production

```bash
npm start
```

## API Documentation

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-14T10:30:00Z",
  "services": {
    "data-service": "up",
    "ai-service": "up"
  }
}
```

### Company Endpoints

```http
GET /api/v1/companies/{symbol}
```

Gets company information from data-service.

### Financial Data Endpoints

```http
GET /api/v1/financials/{symbol}/quarterly
GET /api/v1/financials/{symbol}/annual
GET /api/v1/prices/{symbol}?days=30
GET /api/v1/news/{symbol}
```

### Analysis Endpoints

```http
POST /api/v1/debate/start
{
  "symbol": "MBB",
  "includeAnalysis": ["fundamental", "technical", "sentiment"]
}

GET /api/v1/debate/{sessionId}

GET /api/v1/debate/{sessionId}/status
```

### Session Endpoints

```http
GET /api/v1/sessions
POST /api/v1/sessions/{sessionId}/rate
GET /api/v1/sessions/{sessionId}/export
```

## Directory Structure

```
backend/
├── src/
│   ├── index.js              # Express app entry point
│   ├── config/
│   │   └── index.js          # Configuration management
│   ├── middleware/
│   │   ├── auth.js           # Authentication middleware
│   │   ├── errorHandler.js   # Error handling middleware
│   │   ├── logger.js         # Logging middleware
│   │   └── validator.js      # Request validation
│   ├── routes/
│   │   ├── health.js         # Health check routes
│   │   ├── companies.js      # Company info routes
│   │   ├── financials.js     # Financial data routes
│   │   ├── analysis.js       # Debate/analysis routes
│   │   └── sessions.js       # Session management routes
│   ├── services/
│   │   ├── dataServiceClient.js  # Data service communication
│   │   ├── aiServiceClient.js    # AI service communication
│   │   ├── sessionManager.js     # Session management logic
│   │   └── errorMapper.js        # Error mapping utilities
│   └── utils/
│       ├── logger.js         # Logging utilities
│       ├── errors.js         # Custom error classes
│       └── validators.js     # Validation utilities
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data
├── .env.example              # Environment template
├── .eslintrc.json            # ESLint config
├── package.json              # Dependencies
├── Dockerfile                # Container definition
└── README.md                 # This file
```

## Code Quality

- **Type Safety**: JSDoc comments for type hints
- **Error Handling**: Comprehensive try-catch with meaningful error responses
- **Logging**: Structured logging at multiple levels (DEBUG, INFO, WARN, ERROR)
- **Testing**: Unit and integration test coverage
- **Linting**: ESLint for code quality

## Development Workflow

1. Review task requirements
2. Check API contracts with data-service and ai-service
3. Implement routes with proper error handling
4. Add comprehensive logging
5. Write unit and integration tests
6. Update API documentation
7. Test with frontend team

## Common Patterns

### Error Handling

```javascript
try {
  const data = await dataServiceClient.getCompany(symbol);
  res.json(data);
} catch (error) {
  logger.error(`Error fetching company: ${error.message}`);
  res.status(500).json({ 
    error: 'Failed to fetch company data',
    message: error.message 
  });
}
```

### Service Communication

```javascript
const response = await axios.get(
  `${process.env.DATA_SERVICE_URL}/api/v2/company/${symbol}`,
  { timeout: 10000 }
);
```

## Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Specific test file
npm test -- --testPathPattern=companies
```

## Contributing

Follow the development workflow defined in AGENT_ROLES.md for the backend engineer role.

## License

MIT
