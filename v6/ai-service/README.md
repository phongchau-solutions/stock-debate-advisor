# AI Service - Multi-Agent Debate Orchestration

**Production-Ready FastAPI Service** for orchestrating multi-agent stock debate using CrewAI. Integrates with data-service and frontend via REST APIs.

## 🎯 Features

- **FastAPI REST API** - High-performance, auto-documented endpoints
- **CrewAI Framework** - Specialized multi-agent orchestration
- **5 Agent Roles** - Fundamental, Technical, Sentiment Analysts + Moderator & Judge
- **Dynamic Debate Rounds** - Judge determines optimal number of rounds (10-50)
- **Persistent Sessions** - Database-backed debate history
- **Streaming Responses** - Real-time message streaming to frontend
- **Docker Ready** - Local dev and production deployment
- **AWS Integration** - ECS Fargate, Lambda, API Gateway support
- **Health Checks** - Built-in monitoring and status endpoints

## 📋 Architecture

```
┌─────────────┐
│   Frontend  │ (React, port 3000)
└──────┬──────┘
       │
       │ REST API
       ▼
┌──────────────────────┐
│  AI Service (FastAPI)│ (Port 8000)
│  - Debate Endpoints  │
│  - Streaming Support │
│  - Session Management│
└──────┬───────────────┘
       │
       ├─ Data Service (port 8001)
       │  └─ Financial Data
       │  └─ Company Info
       │
       └─ PostgreSQL
          └─ Session Storage
```

## 🚀 Quick Start

### Local Development (Docker)

```bash
cd v6/ai-service

# Setup environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start services
./scripts/local-dev.sh start

# View services
docker-compose ps

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### Manual Setup (Python)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY="your-api-key"

# Run server
python main.py
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## 📚 API Endpoints

### Health & Info
```bash
GET /              # Service info
GET /health        # Health check
GET /docs          # OpenAPI documentation
GET /redoc         # ReDoc documentation
```

### Data
```bash
GET /api/v1/symbols            # List available stocks
```

### Debate Operations
```bash
POST /api/v1/debate/start      # Start new debate
GET /api/v1/debate/status/{id} # Get debate status
GET /api/v1/debate/result/{id} # Get final verdict
GET /api/v1/debate/stream/{id} # Stream messages (SSE)
```

### Example: Start Debate

```bash
curl -X POST http://localhost:8000/api/v1/debate/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MBB.VN",
    "rounds": 20
  }'

# Response
{
  "session_id": "sess_abc123",
  "symbol": "MBB.VN",
  "status": "running",
  "current_round": 1,
  "total_rounds": 20
}
```

## ⚙️ Configuration

### Environment Variables

```env
# LLM
GEMINI_API_KEY=your-api-key              # Required
CREWAI_MODEL=gemini-2.5-pro              # LLM model
TEMPERATURE=0.7                          # Response creativity
MAX_TOKENS=4096                          # Response length

# Debate
MIN_ROUNDS=10                            # Minimum debate rounds
MAX_ROUNDS=50                            # Maximum debate rounds
DEBATE_ROUNDS=20                         # Default rounds

# Database
DATABASE_URL=postgresql://...            # PostgreSQL connection

# Data Service
DATA_SERVICE_URL=http://localhost:8001   # Data service endpoint

# Logging
LOG_LEVEL=INFO                           # Log verbosity
VERBOSE=True                             # Detailed logging
```

### Create .env File

```bash
cp .env.example .env
nano .env  # Edit with your values
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t stock-debate-ai-service:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e CREWAI_MODEL=gemini-2.5-pro \
  stock-debate-ai-service:latest
```

### Docker Compose (All Services)

```bash
# Start all services (AI, Data, Database)
docker-compose up -d

# View logs
docker-compose logs -f ai-service

# Stop services
docker-compose down
```

## ☁️ AWS Deployment

AWS infrastructure is **managed via AWS CDK** in the `infra/` directory.

### Deploy via CDK (Recommended)

```bash
cd ../infra
npm install
cdk deploy
```

### Manual Deployment (Reference)

For manual testing and reference, see scripts in `scripts/` directory:
- `deploy-ecs.sh` - Manual ECS Fargate deployment
- `deploy-lambda.sh` - Manual Lambda deployment

### Configuration

See [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for:
- CDK-based infrastructure
- Manual deployment reference
- Environment configuration
- Monitoring and logging

## 🧪 Testing

### Health Check

```bash
# Check service is running
curl http://localhost:8000/health
```

### Pytest

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov --cov-report=html
```

### Integration Test

```bash
./scripts/local-dev.sh test
```

## 📊 Monitoring

### Docker Logs

```bash
# AI Service logs
docker-compose logs -f ai-service

# All services
docker-compose logs -f
```

### AWS CloudWatch

```bash
# View logs
aws logs tail /ecs/stock-debate-ai-service --follow

# Create log group
aws logs create-log-group --log-group-name /ecs/stock-debate-ai-service
```

## 🔌 Integration with Data Service

The AI Service calls the backend data service for financial information:

```python
# Data Service Base URL
DATA_SERVICE_URL = "http://data-service:8001"

# Endpoints accessed:
GET /api/v1/financial/{symbol}      # Financial data
GET /api/v1/prices/{symbol}         # Price history
GET /api/v1/news/{symbol}           # News/sentiment
```

Configure via `DATA_SERVICE_URL` environment variable.

## 📖 Documentation

- [Setup & Deployment Guide](./SETUP_GUIDE.md)
- [AWS Deployment Details](./AWS_DEPLOYMENT.md)
- [API Architecture](../API_ARCHITECTURE.md)
- [Agent Roles & Prompts](../../AGENT_ROLES.md)

## 🛠️ Development

### Project Structure

```
ai-service/
├── main.py                  # FastAPI application
├── api_server.py           # API endpoints
├── orchestrator.py         # CrewAI orchestration
├── agents/                 # Agent implementations
├── prompts/                # Agent system prompts
├── config.py               # Configuration
├── models.py               # Pydantic models
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-service setup
├── requirements.txt        # Python dependencies
├── scripts/                # Deployment scripts
│   ├── local-dev.sh       # Local development
│   ├── deploy-ecs.sh      # ECS deployment
│   └── deploy-lambda.sh   # Lambda deployment
└── README.md              # This file
```

### Code Quality

- Type hints throughout (Python 3.11+)
- SOLID principles
- Comprehensive logging
- Error handling
- AWS-ready

## 🔐 Security

- Non-root Docker user
- Environment-based secrets
- HTTPS in production (via API Gateway)
- CORS restrictions
- Rate limiting ready
- Input validation

## ⚡ Performance

- Async/await throughout
- Connection pooling
- Response caching
- Streaming support
- Horizontal scaling ready

## 📝 Logging

All services log to:
- Console (development)
- CloudWatch (AWS)
- Files (optional)

```bash
# View logs with timestamps
docker-compose logs -f --timestamps ai-service
```

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8000

# Use different port
uvicorn main:app --port 8002
```

### API Key Not Working

```bash
# Verify key is set
echo $GEMINI_API_KEY

# Check format
grep GEMINI_API_KEY .env
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps

# Verify connection string
echo $DATABASE_URL
```

## 📞 Support

- **Docs**: `/docs` endpoint in running service
- **GitHub**: Submit issues or PRs
- **Email**: Contact dev team

## 📄 License

See [LICENSE](../../LICENSE) file

---

**Stock Debate Advisor AI Service** | Part of Stock Debate Advisor v6 | January 2026


```bash
# LLM Configuration
GEMINI_API_KEY=your_api_key
LLM_MODEL=gemini-2.5-pro
LLM_TEMPERATURE=0.7

# Service URLs
DATA_SERVICE_URL=http://data-service:8001
```

## API Endpoints

### Debate Orchestration

```bash
# Start a new debate
POST /api/v1/debate
{
  "symbol": "MBB",
  "rounds": 3,
  "context": "Evaluate for Q1 2026 investment decision"
}

# Get debate result
GET /api/v1/debate/{session_id}

# List all sessions
GET /api/v1/sessions

# Get session status
GET /api/v1/sessions/{session_id}/status
```

## Project Structure

```
ai-service/
├── app/
│   ├── agents/          # Agent definitions
│   ├── tools/           # CrewAI tools and integrations
│   ├── tasks.py         # Task definitions for agents
│   └── crew.py          # Crew orchestration
├── api_server.py        # FastAPI server for debate API
├── demo_app.py          # Streamlit interactive UI
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
└── Dockerfile           # Container image
```

## Agent Architecture

### Fundamental Analyst
- Analyzes financial statements (income, balance sheet, cash flow)
- Calculates key ratios (P/E, P/B, ROE, ROIC)
- Evaluates valuation relative to peers
- Assesses company health and sustainability

### Technical Analyst
- Identifies support and resistance levels
- Analyzes technical indicators (RSI, MACD, Moving Averages)
- Recognizes chart patterns (trends, reversals, consolidation)
- Provides price targets and trading signals

### Sentiment Analyst
- Analyzes news sentiment and market psychology
- Identifies key themes and catalysts
- Measures investor sentiment and risk appetite
- Assesses narrative strength and consensus

### Moderator
- Guides the debate structure
- Challenges arguments with counter-questions
- Ensures balanced perspective
- Manages time and depth of analysis

### Judge
- Evaluates all presented arguments
- Weighs evidence from different perspectives
- Provides investment recommendation (BUY/HOLD/SELL)
- Assigns confidence score and key risk factors

## Technology Stack

- **Framework**: CrewAI
- **LLM**: Google Gemini (or OpenAI GPT-4)
- **API**: FastAPI
- **UI**: Streamlit
- **Python**: 3.11+

## Integration with Other Services

- **Data Service**: Fetches financial data, prices, news for analysis
- **Frontend**: Receives debate results for visualization
- **Database**: Stores session history and debate results

## Testing

```bash
# Run API health check
curl http://localhost:8000/health

# Test debate creation
curl -X POST http://localhost:8000/api/v1/debate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "MBB", "rounds": 3}'
```

## Notes

- Requires valid LLM API key (Gemini or OpenAI)
- Data Service must be running for financial data access
- Sessions are stored in database for persistence
- Large debates may take 2-5 minutes depending on LLM latency
