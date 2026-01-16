# Stock Debate Advisor v7 - Technical Architecture

## System Overview

Production-ready serverless multi-agent AI platform for stock analysis debates. Uses AWS Lambda for short debates, ECS Fargate for long-running debates, and AWS Bedrock Claude for AI orchestration.

### Key Improvements (Jan 2024)
- **Frontend API** - Environment-configurable (no localhost hardcoding)
- **Long-Running Debates** - ECS Fargate handles debates >15 minutes
- **Backend Services** - Modular Python services for code organization and security

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React SPA)                       │
│              S3 Bucket + CloudFront (HTTPS)                  │
│         - Environment-configured API endpoint                │
└────────────────────────┬────────────────────────────────────┘
                         │ /api/* CloudFront proxy
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (REST)                          │
│  - CORS enabled (configurable origins)                       │
│  - Rate limiting (50 req/s, 100 burst)                       │
│  - CloudWatch logging and metrics                            │
└─────────┬──────────────────────────────────┬────────────────┘
          │                                  │
      /health                            /debate
          │                                  │
          ↓                                  ↓
    ┌──────────────┐              ┌──────────────────┐
    │ Lambda       │              │ Lambda Wrapper   │
    │ (Health)     │              │ (Submit to SQS)  │
    │ 30s timeout  │              │ Non-blocking     │
    └──────────────┘              │ Returns 202      │
                                  └────────┬─────────┘
                                          │
                                          ↓
                              ┌──────────────────┐
                              │  SQS Queue       │
                              │  (Debate tasks)  │
                              │  20min visibility│
                              └────────┬─────────┘
                                       │ consume
                    ┌──────────────────────────────────┐
                    │  ECS Fargate Cluster             │
                    │  Auto-scaling 1-10 tasks         │
                    │  2vCPU, 8GB RAM per task         │
                    │  15-min timeout (configurable)   │
                    │                                  │
                    │  Multi-agent Debate:             │
                    │  • Fundamental Agent             │
                    │  • Technical Agent               │
                    │  • Sentiment Agent               │
                    │  • Judge Agent (moderator)       │
                    │                                  │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │  Backend Services (Python)     │
                    │                                │
                    │  DebateOrchestrator            │
                    │  - Lifecycle management        │
                    │                                │
                    │  DataService                   │
                    │  - Company/financial/price     │
                    │                                │
                    │  DatabaseClient                │
                    │  - DynamoDB abstraction        │
                    │                                │
                    │  APIRouter                     │
                    │  - Request routing             │
                    │                                │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │  AWS Bedrock                   │
                    │  Claude Sonnet 3.5             │
                    │  (Multi-agent orchestration)   │
                    └────────────────────────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │  AWS DynamoDB                  │
                    │  (Store results & data)        │
                    └────────────────────────────────┘
```

## Component Details

### 1. Frontend (React + TypeScript)
**Stack**: Vite, React 18, TypeScript, Axios
**Deployment**: S3 + CloudFront (global CDN)

**Configuration**:
```
.env.production - Uses VITE_API_BASE_URL environment variable
vite.config.ts  - Build-time API endpoint injection
CloudFront      - /api/* proxy to API Gateway
```

**Features**:
- Stock symbol input & debate submission
- Custom round configuration
- Real-time status polling
- Results display with verdict & confidence
- Session history tracking

### 2. API Gateway
**Type**: REST API with resource-based permissions
**Authentication**: Optional (configurable)
**CORS**: Enabled for CloudFront origin
**Throttling**: 50 req/s (configurable), 100 burst

**Endpoints**:
- `GET /health` → Health check
- `POST /debate` → Submit debate (returns 202 Accepted)
- `GET /debate/{session_id}` → Poll debate status

**Response Codes**:
- `200` - Successful request
- `202` - Debate task submitted (async)
- `400` - Bad request
- `404` - Debate not found
- `500` - Server error

### 3. Compute Layer

#### Lambda Functions (Short-running)
**Debate Health Check Lambda**
- Runtime: Python 3.12
- Timeout: 30 seconds
- Memory: 128 MB
- Purpose: Health/readiness checks

**Debate Submitter Lambda**
- Runtime: Python 3.12
- Timeout: 30 seconds
- Memory: 256 MB
- Purpose: Submit debate task to SQS (non-blocking)

**Data Uploader Lambda**
- Runtime: Python 3.12
- Timeout: 15 minutes
- Memory: 1024 MB
- Purpose: Auto-upload stock data on deployment

#### ECS Fargate (Long-running)
**Task Definition**:
- CPU: 2 vCPU
- Memory: 8 GB
- Image: Python 3.12 + dependencies
- Logging: CloudWatch (/ecs/stock-debate-task)

**Auto-Scaling Policy**:
- Min: 1 task
- Max: 10 tasks (configurable)
- Scale up: When SQS queue depth > 1
- Scale down: When queue is empty

**Process**:
1. Pull message from SQS queue
2. Initialize backend services
3. Fetch company data from DynamoDB
4. Run multi-agent debate via Bedrock
5. Store results in DynamoDB
6. Delete message from queue

### 4. SQS Queue
**Name**: stock-debate-tasks
**Message Retention**: 24 hours
**Visibility Timeout**: 20 minutes
**Purpose**: Decouple task submission from processing

**Message Format**:
```json
{
  "debate_id": "debate_abc123_1234567890",
  "symbol": "MBB",
  "rounds": 3
}
```

### 5. Backend Services (Python)

#### models.py - Data Classes
```python
DebateRecord          # Debate session with results
CompanyRecord         # Stock company metadata
FinancialReportRecord # Quarterly financial data
OhlcPriceRecord       # Historical OHLC prices

Enums:
  DebateStatus  # INITIATED, IN_PROGRESS, COMPLETED, FAILED, TIMEOUT
  Recommendation # BUY, HOLD, SELL
  ConfidenceLevel # LOW, MEDIUM, HIGH
```

#### database.py - DynamoDB Abstraction
```python
DynamoDBClient
  - get_debate_record(debate_id)
  - put_debate_record(record)
  - update_debate_status(debate_id, status, **kwargs)
  - query_debates_by_symbol(symbol)
  - query_financial_reports(symbol)
  - query_ohlc_prices(symbol)
```

**Error Handling**:
- Automatic retries for transient failures
- Detailed CloudWatch logging
- Custom DatabaseError exception

#### orchestrator.py - Debate Lifecycle
```python
DebateOrchestrator
  - initiate_debate(symbol, rounds)     # Create session
  - update_debate_in_progress(debate_id) # Mark started
  - complete_debate(debate_id, verdict, summary, duration)
  - fail_debate(debate_id, error_message)
  - get_debate_status(debate_id)
  - get_debate_results(debate_id)
  - get_debate_history(symbol)
```

#### data_service.py - Data Retrieval
```python
DataService
  - get_company_info(symbol)
  - get_financial_data(symbol)
  - get_price_data(symbol)
  - get_all_company_data(symbol)  # Combined view
```

#### api_router.py - Request Routing
```python
APIRouter
  - start_debate(symbol, rounds)
  - get_debate_status(debate_id)
  - get_debate_results(debate_id)
  - get_company_data(symbol)
  - get_debate_history(symbol)
```

### 6. Data Storage (DynamoDB)

#### Companies Table
```
PK: symbol (String)
Attributes:
  - name: String
  - sector: String
  - industry: String
  - market_cap: Number
  - last_updated: String (ISO 8601)
```

#### FinancialReports Table
```
PK: symbol (String)
SK: report_date (String)
Attributes:
  - report_type: String (BALANCE_SHEET, INCOME_STATEMENT, etc.)
  - metrics: Map (JSON serialized)
  - fetched_at: String (ISO 8601)
```

#### OHLCPrices Table
```
PK: symbol (String)
SK: date (String)
Attributes:
  - open: Number
  - high: Number
  - low: Number
  - close: Number
  - volume: Number
```

#### DebateResults Table
```
PK: debate_id (String)
Attributes:
  - symbol: String
  - status: String (enum)
  - rounds: Number
  - created_at: String (ISO 8601)
  - started_at: String (optional)
  - completed_at: String (optional)
  - verdict: Map (JSON serialized, optional)
  - debate_summary: String (optional)
  - error_message: String (optional)
  - duration_seconds: Number (optional)

TTL Attribute: 30-day auto-deletion
```

## Deployment Modes

### Mode 1: Lambda Only
**When**: Short debates <15 minutes
**Deploy**: `cdk deploy --all`
**Pros**: Simple, low latency, pay-per-request
**Cons**: Hard timeout at 15 minutes

### Mode 2: Lambda + ECS (Recommended)
**When**: Mixed workload (short + long debates)
**Deploy**: `USE_ECS_DEBATES=true cdk deploy --all`
**Pros**: Handles long debates, auto-scaling, cost-efficient
**Cons**: Slight extra complexity with async pattern

## Data Flow Examples

### Example 1: Short Debate (Lambda)
1. Frontend submits → API Gateway → Lambda
2. Lambda orchestrates debate (5-10 min)
3. Results stored in DynamoDB
4. Frontend receives results (blocking)

### Example 2: Long Debate (ECS via SQS)
1. Frontend submits → API Gateway → Lambda Wrapper
2. Lambda submits to SQS, returns 202 Accepted
3. ECS task pulls from SQS
4. ECS orchestrates debate (15+ minutes)
5. Results stored in DynamoDB
6. Frontend polls `/debate/{session_id}` until complete

## Security Architecture

### API Gateway
- ✅ CORS configured for specific origins
- ✅ Throttling enabled (prevent abuse)
- ✅ CloudWatch logging (audit trail)
- ✅ WAF-ready (integrate if needed)

### Lambda Functions
- ✅ IAM roles with least-privilege
- ✅ Bedrock access restricted to Claude models
- ✅ DynamoDB access scoped to specific tables
- ✅ VPC optional (for private databases)

### ECS Tasks
- ✅ Task role with minimum permissions
- ✅ SQS queue access scoped
- ✅ DynamoDB read/write permissions configured
- ✅ CloudWatch logging enabled

### Data Protection
- ✅ DynamoDB encryption at rest
- ✅ CloudFront HTTPS (TLS 1.2+)
- ✅ S3 bucket blocked from public access
- ✅ API Keys managed in Secrets Manager

## Monitoring & Observability

### CloudWatch Logs
- `/aws/lambda/stock-debate-advisor-compute-prod` - Lambda logs
- `/ecs/stock-debate-task` - ECS task logs
- `/aws/apigateway/stock-debate-api` - API Gateway logs

### CloudWatch Metrics
- Lambda invocations, duration, errors
- ECS task count, CPU, memory
- SQS queue depth, messages processed
- DynamoDB read/write capacity, throttles
- API Gateway requests, latency, errors

### Alarms (Recommended)
- ECS task failure rate > 10%
- SQS queue depth > 100
- API Gateway 5xx errors > 1%
- DynamoDB throttled requests > 0

## Cost Optimization

### Cost Drivers
- **Lambda**: $0.0000002 per request + $0.000016667 per GB-second
- **ECS**: $0.04 per hour (2vCPU, 8GB, on-demand)
- **DynamoDB**: PAY_PER_REQUEST ($1.25 per M writes, $0.25 per M reads)
- **CloudFront**: $0.085 per GB (first 10TB/month)
- **API Gateway**: $3.50 per M requests

### Optimization Strategies
1. **Use Lambda for short debates** (no ECS running)
2. **Set ECS max tasks conservatively** (e.g., 5 instead of 10)
3. **Enable DynamoDB auto-scaling** (not pay-per-request)
4. **Use CloudFront caching** (30-day TTL for company data)
5. **Set debate result TTL** (30 days default)

## Scalability Limits

| Component | Limit | Notes |
|-----------|-------|-------|
| Lambda | 1000 concurrent | Can request increase |
| ECS Fargate | 10 tasks default | Configurable via CDK |
| SQS Queue | Unlimited | Messages, not requests |
| DynamoDB | Unlimited | On-demand billing |
| API Gateway | 10K req/s | Can request increase |
| CloudFront | Global | Unlimited edge locations |

## Disaster Recovery

### Backup Strategy
- DynamoDB: Point-in-time recovery (PITR) enabled for production
- Frontend: Versioned S3 bucket (retain old versions)
- Code: Git history (GitHub)

### Recovery Procedures
1. **Data Loss**: Restore DynamoDB from PITR
2. **API Outage**: Rerun `cdk deploy`
3. **Frontend Issue**: Roll back S3 version or CloudFront cache invalidation
4. **Complete Failure**: `cdk destroy && cdk deploy`

## Future Enhancements

1. **Authentication**: Add Cognito User Pools for user management
2. **Real-time Updates**: WebSocket API for live debate progress
3. **Analytics Dashboard**: CloudWatch dashboards for debate trends
4. **Multi-region**: Deploy to multiple regions for low-latency
5. **Cache Layer**: ElastiCache for frequent data queries
6. **Search**: OpenSearch for debate history search

---

**Version**: 7.1 | **Updated**: January 2024 | **Status**: ✅ Production Ready
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
