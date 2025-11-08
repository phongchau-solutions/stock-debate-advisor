# Autogen Multi-Agent Financial Debate POC (v3)

**Production-aligned Vietnamese Stock Market Investment Decision System**

This is a fully integrated proof-of-concept demonstrating Microsoft Autogen orchestrating multi-agent debates with real Vietcap API integration, dynamic moderator flow, and live Streamlit visualization.

## 🎯 Features

- ✅ **Microsoft Autogen Integration**: Full `autogen-agentchat` framework integration
- ✅ **Real Vietcap Data**: Live Vietnamese stock market data with retry/caching
- ✅ **Dynamic Debate Flow**: Moderator dynamically orchestrates agent speaking order
- ✅ **Multi-Agent Analysis**: Technical, Fundamental, and Sentiment agents
- ✅ **Live Streamlit UI**: Color-coded real-time debate visualization
- ✅ **Structured Logging**: Complete debate transcripts saved to `/logs`
- ✅ **Python 3.11**: Compatible with modern Python environments
- ✅ **Docker Ready**: Full containerization support

## 🚀 Quick Start

### Option 1: Local Python Environment (Recommended)

**Prerequisites**: Python 3.11

```bash
# Navigate to project
cd v3/autogen_debate_poc

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py
```

Open browser: http://localhost:8501

### Option 2: Docker

```bash
cd v3/autogen_debate_poc

# Build and run
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

Open browser: http://localhost:8501

## 📋 System Architecture

### Agents

| Agent | Role | Data Sources | Output |
|-------|------|--------------|--------|
| **TechnicalAnalyst** | Price trends, technical indicators | Vietcap OHLCV, yfinance fallback | BUY/HOLD/SELL signal with RSI, MACD, Bollinger Bands |
| **FundamentalAnalyst** | Financial ratios, valuation | Vietcap financials | Undervalued/Overvalued assessment with P/E, ROE, fair value |
| **SentimentAnalyst** | News sentiment analysis | VnEconomy, WSJ articles | Positive/Neutral/Negative sentiment with themes |
| **Moderator** | Debate orchestration | All agent outputs | Synthesized consensus recommendation |

### Services

- **VietcapService**: Real-time Vietnamese stock data with async fetching, retry logic, caching
- **PromptService**: Dynamic prompt template management and data injection
- **DebateOrchestrator**: Multi-round debate coordination with transcript logging

### Debate Flow

1. **Preparation**: Fetch data from Vietcap API (with yfinance fallback)
2. **Agent Initialization**: Load prompts, inject data, create agents
3. **Round 1**: Standard order (Technical → Fundamental → Sentiment)
4. **Rounds 2-N**: Moderator dynamically selects speakers
5. **Final Round**: Moderator synthesizes consensus
6. **Logging**: Save complete transcript to `/logs`

## 🔧 Configuration

### Optional: Gemini API Key

For real LLM-powered analysis (optional):

1. Get API key from https://makersuite.google.com/app/apikey
2. Enter in Streamlit sidebar "LLM Settings"

Without API key, system runs with synthetic analysis (demo mode).

### Environment Variables (Optional)

Create `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
VIETCAP_API_KEY=your_vietcap_key_here  # Optional
```

## 📁 Project Structure

```
v3/autogen_debate_poc/
├── agents/
│   ├── technical_agent.py      # Technical analysis with indicators
│   ├── fundamental_agent.py    # Financial ratio analysis
│   ├── sentiment_agent.py      # News sentiment analysis
│   └── moderator_agent.py      # Debate orchestration
├── services/
│   ├── vietcap_service.py      # Stock data integration
│   ├── prompt_service.py       # Prompt management
│   └── debate_orchestrator.py  # Debate coordination
├── prompts/
│   ├── technical_prompt.txt    # Technical agent prompt
│   ├── fundamental_prompt.txt  # Fundamental agent prompt
│   ├── sentiment_prompt.txt    # Sentiment agent prompt
│   └── moderator_prompt.txt    # Moderator prompt
├── logs/                        # Debate transcripts
├── data/staging/                # Cached stock data
├── app.py                       # Streamlit UI
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## 🧪 Testing

Test with Vietnamese stock symbol:

```bash
# In Streamlit UI:
Stock Symbol: VNM  # Vinamilk
Period: 30 days
Rounds: 5

Click "Start Debate"
```

Expected output:
- Live debate feed with color-coded agents
- Final recommendation: BUY/HOLD/SELL
- Confidence score
- Downloadable transcript

## 📊 Sample Output

```
[Round 1] TechnicalAnalyst
Signal: BUY | Confidence: 75%
RSI at 28.5 (oversold). MACD bullish with histogram at 2.34. Price at 15% of Bollinger Band range.

[Round 2] FundamentalAnalyst
Valuation: UNDERVALUED | Confidence: 70%
P/E ratio of 11.2 below market average. ROE of 16.8% indicates strong profitability. Fair value estimate suggests 12.5% upside.

[Round 3] SentimentAnalyst
Sentiment: POSITIVE | Confidence: 60%
Overall market sentiment is positive based on 5 articles. Key themes: Strong Q3 earnings, Market expansion.

[Final] Moderator
🎯 FINAL DECISION: BUY
Confidence: 73%
After comprehensive multi-agent analysis, recommendation is BUY. Supporting agents: Technical, Fundamental.
```

## 📝 Production Improvements (Documented for Next Phase)

### Phase 1: Data Integration
- [ ] Full Vietcap API authentication and rate limiting
- [ ] Production-grade web crawlers for VnEconomy/WSJ with robotstxt compliance
- [ ] Real-time data streaming vs batch fetching
- [ ] Historical data storage in PostgreSQL/TimescaleDB

### Phase 2: LLM Enhancement
- [ ] Full Google Gemini integration with streaming
- [ ] Prompt versioning and A/B testing
- [ ] Chain-of-thought reasoning for complex decisions
- [ ] Multi-model ensemble (Gemini + Claude + GPT)

### Phase 3: Observability
- [ ] OpenTelemetry instrumentation
- [ ] Prometheus metrics (debate duration, consensus rates, API latency)
- [ ] Structured logging with correlation IDs
- [ ] Error tracking with Sentry

### Phase 4: Scalability
- [ ] Kubernetes deployment with autoscaling
- [ ] Redis caching layer
- [ ] Airflow DAGs for scheduled analysis
- [ ] Multi-market support (Thailand, Singapore, Indonesia)

### Phase 5: Quality Assurance
- [ ] Unit tests for all agents (pytest)
- [ ] Integration tests for debate flow
- [ ] Load testing (Locust)
- [ ] CI/CD pipeline (GitHub Actions)

## 🤝 Contributing

This is a proof-of-concept. For production deployment:

1. Implement full Vietcap API authentication
2. Add comprehensive error handling
3. Implement rate limiting and backoff strategies
4. Add user authentication and session management
5. Deploy with proper secrets management (AWS Secrets Manager, Vault)

## 📄 License

Internal VMO Project - Confidential

---

**Success Criteria** ✅

- [x] Functional autogen-agentchat integration
- [x] Vietcap API live data (with fallback)
- [x] Prompt modules and services functional
- [x] Moderator-driven multi-round debate
- [x] Streamlit displaying full debate transcript
- [x] Dockerfile compatible with Python 3.11
- [x] Logs correctly written to `/logs`

**Ready for Demo**: Stock "VNM", Period "30 days"
