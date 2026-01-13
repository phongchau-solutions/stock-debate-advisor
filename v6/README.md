# Stock Debate Advisor - v6 Microservices Architecture

A comprehensive microservices-based system for orchestrating multi-agent stock debate using Google Agent Development Kit (ADK), with data pipeline, analysis engines, and agentic orchestration.

## 🏗️ Architecture Overview

```
v6/
├── data-service/          # Data retrieval and storage
├── analysis-service/      # Analysis engines (Fundamental, Technical, Sentiment)
├── agentic-service/       # Multi-agent debate orchestration (Google ADK)
├── frontend/              # React web UI
└── docker-compose.yml     # Container orchestration
```

## 🚀 Features

### Data Service
- **Data Pipeline**: Airflow DAGs for scheduled data retrieval
- **Yahoo Finance API Integration**: Fetch comprehensive financial data, price history, and metrics
- **News Crawling**: Crawl Vietnamese financial news (VietStock, CafeF, VnEconomy)
- **Database**: PostgreSQL for structured data, MongoDB for documents
- **FastAPI Endpoints**: RESTful API for data access

### Analysis Service
- **Fundamental Analysis**: Financial statement analysis, ratios, valuation
- **Technical Analysis**: Price trends, indicators (RSI, MACD, MA), patterns
- **Sentiment Analysis**: News sentiment, keyword extraction, themes
- **ETL Pipeline**: Process and analyze data from data-service
- **FastAPI Endpoints**: Analysis API with caching

### Agentic Service
- **Google Agent Development Kit (ADK)**: Code-first multi-agent orchestration framework
- **LlmAgent Pattern**: Each analyst as specialized LlmAgent with role-specific instructions
- **Coordinator Agent**: Parent agent managing sub-agents in hierarchical structure
- **Multi-Agent Debate**: Structured debates with Fundamental, Technical, Sentiment analysts + Moderator + Judge
- **Session Management**: ADK sessions for conversation state and memory
- **Tools Layer**: Access to data and analysis services
- **Streamlit Demo**: Working interactive demo UI

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
- **Agentic Service Demo**: http://localhost:8501 (Streamlit UI)
- **Data Service API**: http://localhost:8001/docs
- **Analysis Service API**: http://localhost:8002/docs
- **Airflow UI**: http://localhost:8080 (admin/admin)

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

# Analysis Service
cd analysis-service/
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# Agentic Service
cd agentic-service/
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
- [analysis-service/README.md](./analysis-service/README.md) - Analysis service documentation
- [agentic-service/README.md](./agentic-service/README.md) - Agentic service documentation
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

### Analysis Service API

```bash
# Comprehensive analysis
POST /api/v1/analyze/{symbol}

# Fundamental analysis only
POST /api/v1/fundamental/{symbol}

# Technical analysis only
POST /api/v1/technical/{symbol}

# Sentiment analysis only
POST /api/v1/sentiment/{symbol}
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
Agentic Service (Google ADK) ↔ Analysis Service ↔ Data Service
    ↑                              ↑                   ↑
    └──────────────────────┬───────┘───────────────────┘
                           ↓
                    PostgreSQL + MongoDB
```

## 📝 Environment Variables

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key  # Alternative

# Database
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/stock_debate_data
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=stock_debate

# Service URLs
DATA_SERVICE_URL=http://data-service:8001
ANALYSIS_SERVICE_URL=http://analysis-service:8002

# LLM Configuration
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
```

## 📚 Technology Stack

- **Orchestration**: Google Agent Development Kit (ADK)
- **LLM**: Google Gemini (or OpenAI GPT-4)
- **Backend**: FastAPI, Python 3.11
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL, MongoDB
- **Pipeline**: Apache Airflow
- **Deployment**: Docker, Docker Compose

## 🧪 Testing

```bash
# Test data service
curl http://localhost:8001/health

# Test analysis service
curl http://localhost:8002/health

# Test frontend
npm run test          # Jest unit tests
npm run cypress       # E2E tests
```

## 📄 License

MIT License

---

**Built with Google Agent Development Kit (ADK) and modern microservices architecture**
