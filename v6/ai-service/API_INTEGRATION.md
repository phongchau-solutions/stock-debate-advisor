# AI Service - API Architecture & Integration Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                      Port: 3000 / 8501                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                    REST API / Streaming
                             │
┌────────────────────────────▼────────────────────────────────┐
│               AI Service (FastAPI)                           │
│                      Port: 8000                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Routes:                                               │ │
│  │  - GET  /health                (Load Balancer)         │ │
│  │  - GET  /                      (Service Info)          │ │
│  │  - GET  /docs                  (OpenAPI)              │ │
│  │  - GET  /api/v1/symbols        (List Stocks)          │ │
│  │  - POST /api/v1/debate/start   (Start Debate)         │ │
│  │  - GET  /api/v1/debate/status  (Check Status)         │ │
│  │  - GET  /api/v1/debate/result  (Get Result)           │ │
│  │  - GET  /api/v1/debate/stream  (Stream Messages)      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Internal Components:                                  │ │
│  │  - CrewAI Orchestrator                                 │ │
│  │  - 5 Agent Roles (Analysts + Moderator + Judge)        │ │
│  │  - Session Management                                  │ │
│  │  - Knowledge Manager (Persistent Data)                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────┬──────────────────────────────┬──────────────────────┘
       │                              │
       │ Financial Data               │ Session Storage
       │ Price History                │
       │ News/Sentiment               │
       │                              │
┌──────▼──────────┐           ┌──────▼──────────┐
│  Data Service   │           │   PostgreSQL    │
│  Port: 8001     │           │   Database      │
└─────────────────┘           └─────────────────┘
```

## API Endpoints

### 1. Health & Status

```bash
# Health check (for load balancers)
GET /health

# Response
{
  "status": "healthy",
  "service": "Stock Debate Advisor API",
  "version": "2.0.0",
  "features": {
    "debate_orchestration": true,
    "knowledge_persistence": true,
    "streaming_responses": true,
    "multi_agent_support": true
  }
}
```

### 2. Service Information

```bash
# Get service info
GET /

# Response
{
  "service": "Stock Debate Advisor API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "symbols": "/api/v1/symbols",
    "debate": "/api/v1/debate/start"
  }
}
```

### 3. Get Available Symbols

```bash
GET /api/v1/symbols

# Response
{
  "symbols": ["MBB.VN", "VCB.VN", "FPT.VN", "TCB.VN", "ACB.VN", ...],
  "count": 30
}
```

### 4. Start Debate Session

```bash
POST /api/v1/debate/start
Content-Type: application/json

{
  "symbol": "MBB.VN",
  "rounds": 20
}

# Response
{
  "session_id": "sess_abc123def456",
  "symbol": "MBB.VN",
  "rounds": 20,
  "status": "running",
  "created_at": "2026-01-14T10:30:00",
  "current_round": 1,
  "data_loaded": true
}
```

### 5. Get Debate Status

```bash
GET /api/v1/debate/status/{session_id}

# Response
{
  "session_id": "sess_abc123def456",
  "symbol": "MBB.VN",
  "status": "in_progress",
  "current_round": 5,
  "total_rounds": 20,
  "progress": 25
}
```

### 6. Get Debate Result

```bash
GET /api/v1/debate/result/{session_id}

# Response
{
  "session_id": "sess_abc123def456",
  "symbol": "MBB.VN",
  "status": "completed",
  "verdict": "BUY",
  "confidence": 8,
  "target_price": 32500,
  "summary": "Strong fundamentals with positive sentiment...",
  "agent_arguments": [
    {
      "agent": "Fundamental Analyst",
      "position": "BUY",
      "key_points": [...]
    },
    ...
  ]
}
```

### 7. Stream Debate Messages (SSE)

```bash
GET /api/v1/debate/stream/{session_id}

# Response (Server-Sent Events stream)
event: round_start
data: {"round": 1, "agents": ["Fundamental Analyst"]}

event: agent_message
data: {"agent": "Fundamental Analyst", "message": "...analysis..."}

event: round_end
data: {"round": 1, "consensus": "HOLD"}

event: debate_complete
data: {"verdict": "BUY", "confidence": 8}
```

## Integration with Data Service

The AI Service integrates with the backend data service via HTTP calls:

### Endpoints Called

```bash
# Get financial data
GET {DATA_SERVICE_URL}/api/v1/financial/{symbol}

# Get price history
GET {DATA_SERVICE_URL}/api/v1/prices/{symbol}?days=365

# Get news/sentiment
GET {DATA_SERVICE_URL}/api/v1/news/{symbol}
```

### Configuration

```env
DATA_SERVICE_URL=http://data-service:8001  # Local (Docker)
DATA_SERVICE_URL=https://api.example.com   # Production
```

### Error Handling

If data service is unavailable:
- Falls back to cached data (if available)
- Returns 503 Service Unavailable
- Logs error for monitoring

## Request/Response Models

### DebateRequest

```python
{
  "symbol": str        # Stock symbol (e.g., "MBB.VN")
  "rounds": int        # Number of debate rounds (10-50)
}
```

### DebateSessionResponse

```python
{
  "session_id": str    # Unique session identifier
  "symbol": str        # Stock symbol
  "rounds": int        # Total rounds
  "status": str        # "running", "completed", "error"
  "created_at": str    # ISO timestamp
  "current_round": int # Current round number
  "data_loaded": bool  # Whether data is ready
}
```

### DebateResultResponse

```python
{
  "session_id": str
  "symbol": str
  "status": str
  "verdict": str       # "BUY", "HOLD", "SELL"
  "confidence": int    # 1-10 scale
  "target_price": float
  "summary": str
  "agent_arguments": [
    {
      "agent": str
      "position": str
      "key_points": [str]
      "confidence": int
    }
  ]
  "completed_at": str
}
```

## Authentication & Security

### Current Implementation (Development)

- CORS enabled for all origins (development)
- No API key requirement

### Production Implementation

```python
# Add API key authentication
@app.get("/api/v1/symbols")
async def get_symbols(api_key: str = Header(...)):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... continue
```

### Rate Limiting (Recommended)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/debate/start")
@limiter.limit("5/minute")
async def start_debate(...):
    pass
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Debate started successfully |
| 400 | Bad Request | Invalid symbol or rounds |
| 404 | Not Found | Session ID doesn't exist |
| 500 | Server Error | Unexpected error |
| 503 | Unavailable | Data service down |

### Error Response Format

```json
{
  "error": "Description of what went wrong",
  "status": "error",
  "request_path": "/api/v1/debate/start"
}
```

## Deployment Scenarios

### Local Development

```bash
docker-compose up -d
# Access at http://localhost:8000
```

### AWS ECS Fargate

```bash
./scripts/deploy-ecs.sh production latest
# Managed container orchestration
# Auto-scaling
# Load balancing via AWS NLB
```

### AWS Lambda

```bash
./scripts/deploy-lambda.sh production
# Serverless (pay-per-request)
# 15-minute timeout limit
# Requires API Gateway setup
```

## Performance Metrics

### Expected Response Times

| Endpoint | Time |
|----------|------|
| `/health` | 10ms |
| `/api/v1/symbols` | 50ms |
| `/api/v1/debate/start` | 200ms |
| `/api/v1/debate/status` | 100ms |
| First message streaming | 2-5s |

### Throughput

- **Development**: 10-50 req/sec
- **Production (ECS)**: 100-500 req/sec (scaled)
- **AWS Lambda**: 1000+ concurrent (auto-scaled)

## Monitoring & Observability

### CloudWatch Logs (AWS)

```bash
# View logs
aws logs tail /ecs/stock-debate-ai-service --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/stock-debate-ai-service \
  --filter-pattern "ERROR"
```

### Health Checks

```bash
# Local
curl http://localhost:8000/health

# Production (AWS)
curl https://api.stock-debate-advisor.com/health
```

### Metrics to Monitor

- Request latency (p50, p95, p99)
- Error rate (5xx, 4xx)
- Debate completion rate
- Session duration
- Agent response times
- Data service availability

## Testing

### Unit Tests

```bash
pytest tests/test_api.py -v
```

### Integration Tests

```bash
python test_api.py
```

### Load Testing

```bash
# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health

# Using Apache Bench
ab -n 1000 -c 100 http://localhost:8000/health
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs ai-service

# Verify dependencies
docker-compose ps

# Rebuild image
docker-compose build --no-cache ai-service
```

### API Returns 500 Error

```bash
# Check service health
curl http://localhost:8000/health

# View detailed logs
docker-compose logs -f --tail=100 ai-service

# Check data service is running
curl http://localhost:8001/health
```

### Debate Not Progressing

```bash
# Check session status
curl http://localhost:8000/api/v1/debate/status/{session_id}

# View agent logs
docker-compose logs ai-service | grep "Round"
```

## API Documentation

Automatic documentation available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Additional Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [CrewAI Docs](https://github.com/joaomdmoura/crewAI)
- [Setup Guide](./SETUP_GUIDE.md)
- [AWS Deployment](./AWS_DEPLOYMENT.md)
