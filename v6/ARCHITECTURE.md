# Stock Debate Advisor v6 - Architecture Documentation

## System Architecture

### Overview
v6 is a microservices-based agentic system for stock analysis using multi-agent debates. The system is composed of three main services that communicate via REST APIs, with shared infrastructure for data storage and pipeline orchestration.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌────────────────────┐        ┌──────────────────────┐        │
│  │  Streamlit Demo    │        │  Future Web UI       │        │
│  │  (Port 8501)       │        │  (React/Vue)         │        │
│  └─────────┬──────────┘        └──────────────────────┘        │
└────────────┼─────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                      Agentic Service Layer                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Google Agent Development Kit (ADK)                       │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │   │
│  │  │ Fundamental │  │  Technical   │  │   Sentiment     │ │   │
│  │  │   Analyst   │  │   Analyst    │  │   Analyst       │ │   │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘ │   │
│  │  ┌─────────────┐  ┌──────────────┐                      │   │
│  │  │  Moderator  │  │    Judge     │                      │   │
│  │  └─────────────┘  └──────────────┘                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Orchestration Layer                                      │   │
│  │  - Debate Orchestrator                                    │   │
│  │  - Agent Memory Management                                │   │
│  │  - MCP Integration (Future)                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Port: 8003 (API), 8501 (Streamlit)                             │
└──────────────────────┬───────────────────────────────────────────┘
                       │
           ┌───────────┴────────────┐
           │                        │
┌──────────▼───────────┐  ┌────────▼──────────────┐
│  Analysis Service    │  │    Data Service       │
│  ┌────────────────┐  │  │  ┌──────────────────┐ │
│  │ Fundamental    │  │  │  │  VietCap Client  │ │
│  │ Analyzer       │  │  │  │                  │ │
│  ├────────────────┤  │  │  ├──────────────────┤ │
│  │ Technical      │  │  │  │  News Crawler    │ │
│  │ Analyzer       │  │  │  │  - VietStock     │ │
│  ├────────────────┤  │  │  │  - CafeF         │ │
│  │ Sentiment      │  │  │  │  - VnEconomy     │ │
│  │ Analyzer       │  │  │  ├──────────────────┤ │
│  ├────────────────┤  │  │  │  yFinance        │ │
│  │ ETL Pipeline   │  │  │  │  Integration     │ │
│  └────────────────┘  │  │  └──────────────────┘ │
│  Port: 8002          │  │  Port: 8001           │
└──────────┬───────────┘  └──────────┬────────────┘
           │                         │
           │              ┌──────────▼────────────┐
           │              │  Airflow Scheduler    │
           │              │  ┌──────────────────┐ │
           │              │  │ Financial Data   │ │
           │              │  │ Pipeline DAG     │ │
           │              │  └──────────────────┘ │
           │              │  Port: 8080           │
           │              └───────────┬───────────┘
           │                          │
           └─────────┬────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼──────────┐  ┌────────▼─────────┐
│   PostgreSQL      │  │    MongoDB       │
│   - Financial     │  │   - Debate       │
│     Data          │  │     Transcripts  │
│   - Price Data    │  │   - Analysis     │
│   - News          │  │     Cache        │
│   - Pipeline Logs │  │   - Agent Memory │
│   Port: 5432      │  │   Port: 27017    │
└───────────────────┘  └──────────────────┘
```

## Component Details

### 1. Data Service

**Responsibility**: Data acquisition, storage, and retrieval

**Key Components**:
- **VietCap API Client**: Fetches financial statements, ratios, and company data
- **News Crawler**: Scrapes financial news from Vietnamese sources
- **yFinance Integration**: Historical price data
- **Database Models**: SQLAlchemy models for structured data
- **FastAPI Endpoints**: RESTful API for data access

**Technologies**:
- FastAPI for API framework
- SQLAlchemy for ORM
- BeautifulSoup for web scraping
- Requests for HTTP calls
- Apache Airflow for pipeline orchestration

**Database Schema**:
```
financial_data
├── id (PK)
├── symbol
├── data_type (balance_sheet, income_statement, cash_flow, metrics)
├── period
├── data (JSON)
└── timestamps

price_data
├── id (PK)
├── symbol
├── date
├── open, high, low, close, volume
└── timestamps

news_articles
├── id (PK)
├── symbol
├── title, url, content
├── source
├── sentiment_score
└── timestamps
```

### 2. Analysis Service

**Responsibility**: Data processing and analysis generation

**Key Components**:
- **Fundamental Analyzer**: Financial ratio analysis, valuation, health assessment
- **Technical Analyzer**: Price trend analysis, technical indicators
- **Sentiment Analyzer**: News sentiment analysis, theme extraction
- **ETL Pipeline**: Data transformation and enrichment

**Analysis Methodologies**:

1. **Fundamental Analysis**:
   - Profitability (ROE, ROA, margins)
   - Liquidity (current ratio, quick ratio)
   - Solvency (debt ratios, leverage)
   - Efficiency (asset turnover)
   - Valuation (P/E, P/B ratios)

2. **Technical Analysis**:
   - Trend identification (MA crossovers)
   - Momentum indicators (RSI, MACD)
   - Volume analysis
   - Support/resistance levels

3. **Sentiment Analysis**:
   - Keyword-based sentiment scoring
   - Theme extraction
   - Positive/negative article ratios

**Scoring System**:
- Each methodology produces a 0-100 score
- Weighted combination for overall recommendation
- Clear BUY/SELL/HOLD ratings

### 3. Agentic Service

**Responsibility**: Multi-agent debate orchestration

**Key Components**:

1. **Agent Layer**:
   - **FundamentalAnalyst**: Argues based on fundamentals
   - **TechnicalAnalyst**: Argues based on technicals
   - **SentimentAnalyst**: Argues based on sentiment
   - **Moderator**: Guides debate, challenges arguments
   - **Judge**: Final decision maker

2. **Orchestration Layer**:
   - **DebateOrchestrator**: Manages multi-round debates
   - **Agent Memory**: Maintains conversation context
   - **Tools Integration**: Connects to data/analysis services

3. **Google Agent Development Kit (ADK) Integration**:
   - LlmAgent for each analyst role
   - Hierarchical multi-agent orchestration
   - Coordinator pattern with sub_agents
   - Session-based conversation management

4. **MCP Layer** (Future):
   - Model Context Protocol server
   - Tool registration
   - Context management

**Debate Protocol**:
```
1. Initialization
   ├── Setup agents with system prompts
   ├── Fetch comprehensive analysis data
   └── Prepare debate context

2. Debate Rounds (1 to N)
   ├── Round Start
   │   ├── Fundamental Analyst presents
   │   ├── Technical Analyst presents
   │   ├── Sentiment Analyst presents
   │   └── Moderator responds (except last round)
   └── Round Complete

3. Final Judgment
   ├── Judge reviews all arguments
   ├── Evaluates quality and consistency
   └── Delivers final verdict
```

## Data Flow

### 1. Data Acquisition Flow
```
Airflow Scheduler
    └──> Data Pipeline DAG
         ├──> Fetch VietCap Data
         │    └──> Store in PostgreSQL
         ├──> Crawl News Articles
         │    └──> Store in PostgreSQL
         └──> Fetch Price History
              └──> Store in PostgreSQL
```

### 2. Analysis Flow
```
Analysis Service Request
    └──> Fetch Data from Data Service
         ├──> Financial Data
         ├──> Price Data
         └──> News Data
    └──> Run Analyzers
         ├──> Fundamental Analysis
         ├──> Technical Analysis
         └──> Sentiment Analysis
    └──> Combine Results
         └──> Return Comprehensive Analysis
```

### 3. Debate Flow
```
Agentic Service Request
    └──> Setup Agents
    └──> Fetch Analysis Data
    └──> For Each Round:
         ├──> Analysts Present Arguments
         └──> Moderator Responds
    └──> Judge Provides Final Decision
    └──> Return Debate Transcript
```

## Communication Patterns

### Service-to-Service Communication
- **Protocol**: HTTP/REST
- **Format**: JSON
- **Authentication**: Future (JWT tokens)

### Agent Communication
- **Framework**: Google Agent Development Kit (ADK)
- **Pattern**: Message passing
- **LLM Backend**: Google Gemini or OpenAI

## Scalability Considerations

### Horizontal Scaling
- Each service can be scaled independently
- Load balancers for service endpoints
- Database read replicas for queries

### Caching Strategy
- Redis for analysis results (future)
- MongoDB for debate transcripts
- TTL-based cache invalidation

### Rate Limiting
- Per-service rate limits
- LLM API call throttling
- External API (VietCap) rate management

## Security

### Current Implementation
- Environment variable based secrets
- Docker network isolation
- No public database exposure

### Future Enhancements
- JWT authentication
- API key management
- Role-based access control
- Audit logging
- Encrypted database connections

## Monitoring & Observability

### Proposed Stack
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger

### Key Metrics
- Service response times
- LLM API call latency
- Database query performance
- Debate completion rates
- Agent response quality

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Kubernetes cluster
- Helm charts for deployment
- CI/CD pipeline (GitHub Actions)
- Blue-green deployments

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Google Agent Development Kit (google-adk)
- Apache Airflow

### Databases
- PostgreSQL 15
- MongoDB 7

### LLM
- Google Gemini 1.5 Pro
- OpenAI GPT-4 (alternative)

### Infrastructure
- Docker & Docker Compose
- Nginx (future reverse proxy)
- Kubernetes (production)

### Frontend
- Streamlit (current demo)
- React/Vue (future production UI)

## Future Roadmap

### Phase 1 (Current)
- ✅ Microservices architecture
- ✅ Data pipeline with Airflow
- ✅ Fundamental, technical, sentiment analysis
- ✅ Multi-agent debate with Google ADK
- ✅ Streamlit demo

### Phase 2 (Q1 2026)
- [ ] MCP (Model Context Protocol) integration
- [ ] RESTful API for agentic service
- [ ] Enhanced agent prompts and reasoning
- [ ] Real-time streaming debates
- [ ] WebSocket support

### Phase 3 (Q2 2026)
- [ ] Production web UI (React)
- [ ] User authentication & management
- [ ] Portfolio tracking
- [ ] Historical debate analytics
- [ ] Multi-model ensemble

### Phase 4 (Q3 2026)
- [ ] Advanced technical analysis (TA-Lib)
- [ ] Deep learning sentiment models
- [ ] Real-time news streaming
- [ ] Trading signal generation
- [ ] Backtesting framework

## Conclusion

The v6 architecture provides a robust, scalable foundation for multi-agent stock analysis debates. The clear separation of concerns across microservices, combined with Google Agent Development Kit's powerful orchestration capabilities and built-in tooling, creates a flexible system that can evolve with future requirements.
