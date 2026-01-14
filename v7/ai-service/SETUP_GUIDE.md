# AI Service Setup & Deployment Guide

## Overview

The AI Service is a FastAPI-based microservice that orchestrates multi-agent debates using CrewAI. It integrates with the backend data service and provides REST APIs for the frontend.

**Architecture:**
- FastAPI for REST API endpoints
- CrewAI for multi-agent orchestration
- Google Gemini LLM for agent intelligence
- PostgreSQL for session management
- Docker for containerization
- AWS-ready for cloud deployment

## Local Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Google Gemini API Key
- Node.js 18+ (for frontend development)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/gsx-11/stock-debate-advisor.git
cd stock-debate-advisor/v6/ai-service

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env with your API keys
nano .env
# Required:
# - GEMINI_API_KEY=your-api-key
# - DATABASE_URL=postgresql://user:pass@localhost/db

# 4. Start local services
./scripts/local-dev.sh start

# 5. Verify services are running
docker-compose ps

# 6. Test API
curl http://localhost:8000/health
```

### Manual Setup (without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export GEMINI_API_KEY="your-api-key"
export CREWAI_MODEL="gemini-2.5-pro"

# 4. Run development server
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Running Services

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ai-service

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

### Individual Services

```bash
# AI Service only (port 8000)
docker run -p 8000:8000 --env-file .env stock-debate-ai-service

# With data service (requires both docker-compose files)
docker-compose -f docker-compose.yml up
```

## API Endpoints

### Base URL
- Local: `http://localhost:8000`
- Production: `https://api.stock-debate-advisor.com`

### Health & Info
```bash
# Health check (for load balancers)
GET /health

# Service info
GET /

# OpenAPI documentation
GET /docs
GET /redoc
```

### Debate Endpoints
```bash
# Get available symbols
GET /api/v1/symbols

# Start debate session
POST /api/v1/debate/start
{
  "symbol": "MBB.VN",
  "rounds": 20
}

# Get debate status
GET /api/v1/debate/status/{session_id}

# Get final result
GET /api/v1/debate/result/{session_id}

# Stream debate messages (SSE)
GET /api/v1/debate/stream/{session_id}
```

## Configuration

### Environment Variables

```env
# LLM Configuration
GEMINI_API_KEY=your-api-key
CREWAI_MODEL=gemini-2.5-pro
TEMPERATURE=0.7
MAX_TOKENS=4096

# Debate Configuration
MIN_ROUNDS=10
MAX_ROUNDS=50
DEBATE_ROUNDS=20

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/stock_debate

# Data Service
DATA_SERVICE_URL=http://localhost:8001

# Logging
LOG_LEVEL=INFO
VERBOSE=True

# Deployment
ENVIRONMENT=development
DEBUG=False
```

### Custom Configuration File

Create `.env` file in the ai-service directory:

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

## Deployment

### AWS CDK (Recommended for Production)

AWS infrastructure is managed via **AWS Cloud Development Kit (CDK)**.

```bash
# Navigate to infrastructure directory
cd ../infra

# Install dependencies
npm install

# Deploy to AWS
cdk deploy

# View resources
cdk ls
```

For detailed CDK setup, see [infra/README.md](../infra/README.md)

### Manual Deployment (Testing/Reference)

For manual testing and reference only:

```bash
# ECS Fargate deployment
./scripts/deploy-ecs.sh production latest

# Lambda deployment
./scripts/deploy-lambda.sh production
```

See [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for detailed configuration.

### Docker Deployment

```bash
# Build image
docker build -t stock-debate-ai-service:latest .

# Run container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e CREWAI_MODEL=gemini-2.5-pro \
  stock-debate-ai-service:latest
```

## Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_api.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Integration Tests

```bash
# Test with running services
./scripts/local-dev.sh test

# Manual API testing
curl http://localhost:8000/api/v1/symbols
curl http://localhost:8000/health
```

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/health

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## Monitoring & Logging

### Docker Logs

```bash
# AI Service logs
docker-compose logs -f ai-service

# All services logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 ai-service
```

### CloudWatch (AWS)

```bash
# View logs
aws logs tail /ecs/stock-debate-ai-service --follow

# Create log group
aws logs create-log-group --log-group-name /ecs/stock-debate-ai-service
```

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health | python -m json.tool

# Check with verbose output
curl -v http://localhost:8000/health
```

## Integration with Data Service

The AI Service integrates with the backend data service for financial data:

```python
# Example: Getting stock data
response = requests.get(
    "http://data-service:8001/api/v1/financial/MBB.VN"
)
financial_data = response.json()
```

### Service Discovery

- **Local:** `http://data-service:8001` (via Docker network)
- **Production:** `https://data-service-api.example.com`

Configure via `DATA_SERVICE_URL` environment variable.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8002
```

### API Key Error

```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Check in .env file
grep GEMINI_API_KEY .env

# Set if missing
export GEMINI_API_KEY="your-actual-key"
```

### Docker Network Issues

```bash
# Check network
docker network ls
docker network inspect stock-debate

# Restart services
docker-compose restart
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U postgres -d stock_debate
```

## Performance Optimization

### FastAPI Optimization

```python
# Use uvicorn with multiple workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_session_symbol ON debate_sessions(symbol);
CREATE INDEX idx_session_status ON debate_sessions(status);
```

### Caching

The service includes response caching for:
- Available symbols (cached for 1 hour)
- Symbol metadata (cached for 24 hours)
- Debate templates (cached indefinitely)

## Security

### HTTPS/TLS

In production, ensure:
- API Gateway handles TLS termination
- All internal communication is encrypted
- Secrets stored in AWS Secrets Manager

### API Authentication

Current setup uses CORS for frontend access. For production:
- Implement API key authentication
- Add rate limiting
- Enable WAF rules

### Secret Management

```bash
# Stored in AWS Secrets Manager
aws secretsmanager create-secret \
  --name stock-debate/gemini-api-key \
  --secret-string "your-key"
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review [API_ARCHITECTURE.md](../API_ARCHITECTURE.md)
3. Check [AGENT_ROLES.md](../../AGENT_ROLES.md)
4. Open an issue on GitHub

## Additional Resources

- [AWS Deployment Guide](./AWS_DEPLOYMENT.md)
- [API Architecture](../API_ARCHITECTURE.md)
- [Agent Roles & Prompts](../../AGENT_ROLES.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CrewAI Documentation](https://github.com/joaomdmoura/crewAI)
