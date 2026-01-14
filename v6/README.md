# Stock Debate Advisor - v6 Microservices Architecture

A comprehensive microservices-based system for orchestrating multi-agent stock debate using Google Agent Development Kit (ADK), with data pipeline, analysis engines, and agentic orchestration.

## 🏗️ Architecture Overview

```
v6/
├── ai-service/            # Multi-agent debate orchestration (CrewAI)
├── data-service/          # Data retrieval and storage (Yahoo Finance, News)
├── frontend/              # React web UI (Material Design 3)
├── script/                # Data pipeline and utility scripts
└── docker-compose.yml     # Container orchestration
```

## 🚀 Features

### Data Service
- **Data Pipeline**: Airflow DAGs for scheduled data retrieval
- **Yahoo Finance API Integration**: Fetch comprehensive financial data, price history, and metrics
- **News Crawling**: Crawl Vietnamese financial news (VietStock, CafeF, VnEconomy)
- **Database**: PostgreSQL for structured data, MongoDB for documents
- **FastAPI Endpoints**: RESTful API for data access

### AI Service (CrewAI)
- **CrewAI Framework**: Agent-based orchestration for multi-agent debates
- **Agent Roles**: Fundamental, Technical, Sentiment analysts + Moderator + Judge
- **Multi-Agent Debate**: Structured debates with reasoning and consensus
- **Session Management**: Conversation state and memory management
- **Tools Layer**: Access to data and analysis services
- **Streamlit Demo**: Interactive demo UI for agent interaction
- **API Endpoints**: REST API for debate orchestration

### Frontend
- **React + TypeScript**: Modern web UI with Tailwind CSS
- **Component Library**: Reusable Material Design 3 components
- **Testing**: Jest, Playwright, Cypress
- **State Management**: Jotai atoms
- **API Integration**: Axios with interceptors

## 📦 Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)
- Gemini API Key (or OpenAI API Key)

---

## 🔧 Quick Start

### 1. Clone and Setup

```bash
cd v6/
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start All Services

```bash
# Start all microservices with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access Services

- **Frontend UI**: http://localhost:5173 (React app)
- **AI Service Demo**: http://localhost:8501 (Streamlit UI)
- **Data Service API**: http://localhost:8001/docs

### 4. Run a Debate

1. Open http://localhost:5173 in your browser (or http://localhost:8501 for Streamlit demo)
2. Navigate to Analysis page
3. Enter a stock symbol (e.g., MBB, VNM, VCB)
4. Click "Start Debate"
5. Watch the multi-agent debate unfold!

## 🛠️ Development Setup

### Individual Service Development

```bash
# Data Service
cd data-service/
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# AI Service (CrewAI)
cd ai-service/
pip install -r requirements.txt
streamlit run demo_app.py

# Frontend
cd frontend/
npm install
npm run dev
```

## 📖 Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design and component details
- [QUICKSTART.md](./QUICKSTART.md) - Detailed getting started guide
- [data-service/README.md](./data-service/README.md) - Data service documentation
- [ai-service/README.md](./ai-service/README.md) - AI service (CrewAI) documentation
- [frontend/README.md](./frontend/README.md) - Frontend documentation

## 📊 API Documentation

### Data Service API

```bash
# Get financial data
GET /api/v1/financial/{symbol}

# Get price history
GET /api/v1/prices/{symbol}?days=30

# Get news articles
GET /api/v1/news/{symbol}

# Trigger manual crawl
POST /api/v1/crawl/{symbol}
```

### AI Service API

```bash
# Run multi-agent debate
POST /api/v1/debate
{"symbol": "MBB", "rounds": 3}

# Get debate result
GET /api/v1/debate/{session_id}

# List sessions
GET /api/v1/sessions
```

## 🤖 Agent Architecture

### Agent Roles

1. **Fundamental Analyst**: Analyzes financial statements, ratios, and company health
2. **Technical Analyst**: Analyzes price trends, technical indicators, and patterns
3. **Sentiment Analyst**: Analyzes news sentiment and market psychology
4. **Moderator**: Guides debate, challenges arguments, ensures balance
5. **Judge**: Evaluates all arguments and provides final investment decision

## 🔌 Service Communication

```
Frontend (React)
    ↓
AI Service (CrewAI) ↔ Data Service
    ↑                    ↑
    └────────────────────┘
          ↓
    PostgreSQL + MongoDB
```

## 📝 Environment Variables

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Database
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/stock_debate_data
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=stock_debate

# Service URLs
DATA_SERVICE_URL=http://data-service:8001

# LLM Configuration
LLM_MODEL=gemini-2.5-pro  # or gpt-4
LLM_TEMPERATURE=0.7
```

## 📚 Technology Stack

- **Orchestration**: CrewAI
- **LLM**: Google Gemini (or OpenAI GPT-4)
- **Backend**: FastAPI, Python 3.11
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL, MongoDB
- **Data Pipeline**: Yahoo Finance API, News crawlers
- **Deployment**: Docker, Docker Compose

## 🧪 Testing

```bash
# Test data service
curl http://localhost:8001/health

# Test AI service
curl http://localhost:8000/health

# Test frontend
npm run test          # Jest unit tests
npm run playwright:test   # Playwright E2E tests
```

## 📄 License

MIT License

---

**Built with CrewAI, FastAPI, and modern microservices architecture**
