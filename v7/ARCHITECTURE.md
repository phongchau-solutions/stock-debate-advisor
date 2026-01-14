# Stock Debate Advisor v7 - Architecture

## System Design

### Overview
Serverless multi-agent AI platform for stock analysis debates using AWS Lambda, DynamoDB, and CrewAI.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                     CloudFront + S3                          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────────┐        ┌─────────────────────┐
│  API Gateway        │        │  Cognito            │
│  (REST + CORS)      │        │  (Auth)             │
└──────────┬──────────┘        └─────────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
  POST GET      Authorization
/debates     ← (User Pool)
    │
    ├─────────────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│  Debate Orchestrator     │   │  Data Loader             │
│  Lambda                  │   │  Lambda                  │
│                          │   │                          │
│  - CrewAI debate         │   │  - Fetch stock data      │
│  - Multi-agent analysis  │   │  - Cache in DynamoDB     │
│  - Result persistence    │   │  - TTL management        │
└──────────┬───────────────┘   └──────────┬───────────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │      DynamoDB               │
            │                             │
            │ ┌───────────────────────┐  │
            │ │ Debates Table         │  │
            │ │ - debateId (PK)       │  │
            │ │ - timestamp (SK)      │  │
            │ │ - userId (GSI)        │  │
            │ │ - result              │  │
            │ └───────────────────────┘  │
            │                             │
            │ ┌───────────────────────┐  │
            │ │ Stock Cache Table      │  │
            │ │ - symbol (PK)         │  │
            │ │ - data                │  │
            │ │ - ttl                 │  │
            │ └───────────────────────┘  │
            │                             │
            └─────────────────────────────┘
```

## Components

### 1. Frontend (React + TypeScript)
- **Technology**: Vite, React 18, TypeScript
- **Styling**: CSS3 with responsive design
- **State Management**: React hooks
- **API Client**: Axios with interceptors
- **Features**:
  - Stock symbol input
  - Custom debate questions
  - Real-time result display
  - Export debate results as JSON
  - Authentication UI hooks

### 2. API Gateway
- **Type**: REST API
- **Authentication**: Cognito User Pools
- **CORS**: Configured for all origins (dev) / specific domain (prod)
- **Resources**:
  - `POST /debates` - Create debate
  - `GET /debates?debateId=...` - Get results
  - `GET /data/{symbol}` - Fetch stock data
- **Rate Limiting**: Default AWS limits
- **Logging**: CloudWatch integration

### 3. Lambda Functions

#### Debate Orchestrator (ai-service)
- **Purpose**: Orchestrate multi-agent debate
- **Runtime**: Python 3.12
- **Timeout**: 900 seconds
- **Memory**: 1024 MB
- **Process**:
  1. Receive debate request
  2. Initialize CrewAI agents
  3. Run debate discussion
  4. Store results in DynamoDB
  5. Return debate ID & results
- **Agents**:
  - Fundamental Analyst
  - Technical Analyst
  - Sentiment Analyst
  - Investment Judge

#### Data Loader (data-service)
- **Purpose**: Fetch and cache stock data
- **Runtime**: Python 3.12
- **Timeout**: 60 seconds
- **Memory**: 512 MB
- **Process**:
  1. Receive symbol request
  2. Check DynamoDB cache
  3. If expired, fetch fresh data
  4. Cache with 24-hour TTL
  5. Return stock data

### 4. DynamoDB Tables

#### Debates Table
```
Primary Key: debateId (PK) + timestamp (SK)
Attributes:
  - debateId: String (unique)
  - timestamp: Number (for sorting)
  - userId: String (for GSI)
  - symbol: String
  - question: String
  - result: Map (debate output)
  - status: String (completed/failed)
  - createdAt: String (ISO 8601)

GSI: userIdIndex
  - Partition Key: userId
  - Sort Key: timestamp
```

#### Stock Cache Table
```
Primary Key: symbol (PK)
Attributes:
  - symbol: String
  - data: Map (stock info)
  - ttl: Number (Unix timestamp for expiration)
  - cached_at: String (ISO 8601)
```

### 5. Cognito User Pool
- **Sign-up**: Email-based self-registration
- **Verification**: Automatic email verification
- **Password Policy**: 8+ chars, uppercase, digits
- **OAuth Scopes**: OpenID, email, profile
- **Callbacks**: Localhost (dev) / Custom domain (prod)

### 6. S3 + CloudFront
- **S3 Bucket**: Frontend static files
- **CloudFront**: CDN with caching
- **OAI**: Origin Access Identity
- **Error Handling**: 404/403 → /index.html (SPA routing)
- **Cache Policy**: 
  - index.html: no cache
  - assets: 1 week cache

## Data Flow

### 1. Create Debate
```
Frontend Form
    ↓
POST /debates (with auth)
    ↓
API Gateway + Cognito validation
    ↓
Lambda: Debate Orchestrator
    ├─ Fetch stock data via Data Loader
    ├─ Initialize CrewAI crew
    ├─ Run multi-agent debate (15 min)
    ├─ Store debate in DynamoDB
    └─ Return results
    ↓
Frontend: Display debate results
    ↓
User: Export as JSON
```

### 2. Stock Data Cache
```
GET /data/{symbol}
    ↓
Lambda: Data Loader
    ├─ Query DynamoDB cache
    ├─ Check TTL expiration
    ├─ If expired: Fetch fresh data
    ├─ Update cache with TTL
    └─ Return cached/fresh data
    ↓
Frontend: Display stock info
```

## Security

### Authentication & Authorization
- Cognito User Pools for user management
- JWT tokens in Authorization header
- API Gateway enforces Cognito authorizer
- Lambda functions trust only API Gateway

### Data Protection
- DynamoDB encrypted at rest (AWS managed keys)
- S3 encryption (SSE-S3)
- Secrets Manager for API keys
- HTTPS enforced (CloudFront → S3)

### Network Security
- VPC not required (Lambda functions public)
- API Gateway CORS configured
- CloudFront blocks direct S3 access
- Security headers in CloudFront responses

### Secrets Management
- Gemini API key in AWS Secrets Manager
- Lambda has IAM permission to read secrets
- Not stored in environment files
- Rotatable independently

## Scaling & Performance

### Auto-scaling
- **Lambda**: Automatic concurrent execution scaling
- **DynamoDB**: On-demand billing (automatic scaling)
- **CloudFront**: Global edge locations

### Optimization
- Lambda layer caches dependencies
- DynamoDB TTL auto-deletes old debates
- CloudFront caches frontend assets
- Vite optimizes frontend bundle

### Monitoring
- CloudWatch Logs for Lambda
- CloudWatch Metrics for DynamoDB
- X-Ray tracing available (optional)
- API Gateway detailed metrics

## Cost Optimization

### Pricing Model
- Lambda: Pay per execution (free tier: 1M/month)
- DynamoDB: On-demand mode ($1.25 per million RCU)
- API Gateway: $0.00035 per request
- CloudFront: Data transfer costs
- S3: Storage + requests

### Cost Reduction
- Use on-demand DynamoDB (no capacity planning)
- Set DynamoDB TTL to auto-clean old data
- Use Lambda layer to reduce package size
- Compress CloudFront assets

## Deployment Strategy

### Environments
- **Dev**: Full featured, permissive CORS, smaller resources
- **Prod**: Restricted CORS, monitoring, backup enabled

### CI/CD Ready
- CDK for infrastructure versioning
- Frontend build artifacts
- Lambda layer packaging
- Automated testing hooks

## Future Enhancements

1. **Extended Data Sources**
   - Alpha Vantage API integration
   - News sentiment analysis
   - Social media signals

2. **Advanced Agents**
   - Machine learning models
   - Custom analysis tools
   - External data sources

3. **UI Improvements**
   - Real-time debate streaming
   - Visualization components
   - Mobile app (React Native)

4. **Infrastructure**
   - Multi-region deployment
   - Disaster recovery
   - Cost optimization layers
