# Gemini Multi-Agent Stock Debate PoC - v4

**Minimal, production-ready multi-agent investment decision system** using Microsoft Autogen and Google Gemini API.

Three financial analyst agents (Fundamental, Technical, Sentiment) engage in a structured debate, moderated and judged to produce evidence-based BUY/HOLD/SELL recommendations for Vietnamese stocks.

---

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key
- Docker & Docker Compose (optional)

### Local Setup

```bash
# Clone and navigate
cd /home/x1e3/work/vmo/agentic/v4/autogen_debate_poc

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-api-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/debate_poc"  # Optional

# Run debate on VNM stock
python app.py --stock VNM --rounds 3 --period 30

# Or with custom output
python app.py --stock VIC --rounds 4 --output results/vic_debate.json
```

### Docker Setup

```bash
# Build image
docker build -t gemini-debate-poc .

# Run with environment file
echo "GEMINI_API_KEY=your-key" > .env
docker-compose up

# Or run standalone
docker run -e GEMINI_API_KEY=your-key gemini-debate-poc
```

### Web UI (Streamlit)

```bash
# Install Streamlit
pip install streamlit streamlit-option-menu

# Run interactive demo
streamlit run streamlit_demo.py

# Or use the convenience script
./streamlit_run.sh --api-key "your-api-key-here"
```

Access the web interface at: **http://localhost:8501**

Features:
- 🎯 **Live debate execution** with real-time progress
- 📊 **Stock data visualization** (fundamentals, technicals, charts)
- 📈 **Results dashboard** with verdict breakdown
- 💾 **Export options** (JSON, CSV, Markdown reports)
- ⚙️ **Easy configuration** via sidebar controls

See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed UI documentation.

---

## 🏗️ Architecture

### Folder Structure

```
/agents/                    # Specialist agents
  base_agent.py            # Base class with messaging
  fundamental_agent.py     # Financial analysis expert
  technical_agent.py       # Price/momentum expert
  sentiment_agent.py       # Market sentiment expert
  moderator_agent.py       # Debate facilitator
  judge_agent.py           # Final verdict synthesizer

/services/                  # Core services
  gemini_service.py        # LLM wrapper with retries
  data_service.py          # Stock data aggregation
  debate_orchestrator.py   # Debate flow & coordination

/db/                        # Database layer
  models.py               # SQLAlchemy ORM models

/prompts/                   # Agent system prompts
  fundamental.txt         # Role & expertise definition
  technical.txt
  sentiment.txt
  moderator.txt
  judge.txt

app.py                      # CLI entry point
streamlit_demo.py           # Web UI entry point
streamlit_run.sh            # Streamlit launcher script
Dockerfile                  # Container definition
docker-compose.yml          # Multi-service orchestration
requirements.txt            # Python dependencies
.streamlit/
  config.toml              # Streamlit configuration
```

---

## 🔄 Debate Flow

```
┌─────────────────────────────────────────┐
│ Input: Stock Symbol + Period            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Round 0: Initial Analysis               │
│  ├─ Fundamental: Valuation & financials │
│  ├─ Technical: Momentum & patterns      │
│  └─ Sentiment: News & catalysts         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Rounds 1-3: Debate & Rebuttals         │
│  ├─ Moderator: Synthesis & guidance    │
│  ├─ Each agent: Counter-arguments      │
│  └─ Cross-analysis: Address opposing   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Final Phase: Judge Verdict              │
│  ├─ Moderator: Prepares brief          │
│  ├─ Judge: Weighs evidence (50:25:25)  │
│  └─ Output: JSON decision + rationale   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Result: BUY | HOLD | SELL               │
│ + Confidence, catalysts, risks, horizon │
└─────────────────────────────────────────┘
```

---

## 🧠 Agents & Expertise

### **FundamentalAgent**
- **Data**: P/E ratio, ROE, debt ratio, dividend yield
- **Analysis**: Valuation, financial health, growth prospects
- **Decision Logic**: 
  - BUY: Undervalued + strong ROE + low debt
  - SELL: Overvalued or weak fundamentals
  - HOLD: Fair value or mixed signals

### **TechnicalAgent**
- **Data**: MA-50, MA-200, RSI, MACD, volume trends
- **Analysis**: Trend, momentum, support/resistance
- **Decision Logic**:
  - BUY: Uptrend + bullish indicators (RSI<70, MACD+)
  - SELL: Downtrend + bearish indicators
  - HOLD: Consolidation or mixed signals

### **SentimentAgent**
- **Data**: News sentiment, article count, themes, catalysts
- **Analysis**: Market mood, positive/negative drivers
- **Decision Logic**:
  - BUY: Bullish sentiment + positive catalysts
  - SELL: Bearish sentiment + negative news
  - HOLD: Mixed sentiment or uncertainty

### **ModeratorAgent**
- **Role**: Manage debate structure, enforce rigor
- **Tasks**: 
  - Synthesize round arguments
  - Identify convergence/divergence
  - Guide discussion toward evidence
  - Prepare Judge brief

### **JudgeAgent**
- **Role**: Final decision authority
- **Weighting**:
  - Fundamentals: 50% (long-term drivers)
  - Technicals: 25% (near-term momentum)
  - Sentiment: 25% (market reality)
- **Output**: Structured JSON with decision + rationale

---

## 📊 Decision Output

```json
{
  "stock": "VNM",
  "decision": "BUY",
  "confidence": 0.72,
  "summary": "Stock offers attractive valuation (P/E 13.5) with strong ROE (21%) and positive technical momentum. Market sentiment supports entry despite some near-term headwinds.",
  "rationale": {
    "fundamental": "Undervalued at 13.5x P/E with industry-leading ROE of 21% and conservative leverage.",
    "technical": "Price above both MA-50 and MA-200 with rising volume; RSI at 58 shows healthy momentum.",
    "sentiment": "Positive news flow with 65% positive articles; strong earnings visibility in Q4."
  },
  "key_catalysts": [
    "Q3 2025 earnings beat",
    "Market share gains in key segments",
    "Potential dividend increase"
  ],
  "risks": [
    "Macroeconomic headwinds in Vietnam",
    "New competitor market entry",
    "Currency volatility"
  ],
  "time_horizon": "6-12 months"
}
```

---

## 🗄️ Database Schema

**Optional PostgreSQL persistence** for audit trail and analysis history.

### Tables

- **DebateLog**: Full debate transcript, decision, metadata
- **FinancialAnalysis**: Fundamental metrics snapshots
- **TechnicalAnalysis**: Technical indicators history
- **SentimentAnalysis**: Sentiment scores over time

### Setup

```bash
# Create database (manual)
createdb debate_poc
export DATABASE_URL="postgresql://user:pass@localhost/debate_poc"

# Or use docker-compose (auto-setup)
docker-compose up postgres
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=sk-...

# Optional
DATABASE_URL=postgresql://user:pass@localhost/debate_poc
LOG_LEVEL=INFO
```

### Command-Line Arguments

```bash
python app.py \
  --stock VNM                    # Stock symbol
  --rounds 3                     # Debate rounds (default 3)
  --period 30                    # Historical period days (default 30)
  --output results.json          # Output file (default)
  --api-key sk-...              # Override GEMINI_API_KEY env var
  --db-url postgresql://...     # Override DATABASE_URL env var
```

---

## 🚀 Running the Debate

### Example 1: Simple Local Run

```bash
export GEMINI_API_KEY="your-key"
python app.py --stock VNM --rounds 3
```

**Output**: Logs to `logs/debate.log` + `results.json`

### Example 2: Multi-Stock Batch Analysis

```bash
for stock in VNM VIC VCB; do
  python app.py --stock $stock --rounds 2 --output results/${stock}_debate.json
done
```

### Example 3: Docker Compose (with PostgreSQL)

```bash
export GEMINI_API_KEY="your-key"
export STOCK_SYMBOL="VNM"
export DEBATE_ROUNDS="3"

docker-compose up --build
```

**Services**:
- Debate app: Running debate
- PostgreSQL: Stores results (accessible on `localhost:5432`)

---

## 📈 Success Metrics

✅ **Agents complete 3+ debate rounds** autonomously  
✅ **Moderator manages structured turns** with synthesis  
✅ **Judge produces coherent verdict** grounded in data  
✅ **Results stored in database** with full transcript  
✅ **JSON output validates** against schema  
✅ **Confidence scores are calibrated** (0.5-0.9 typical)  

---

## 🔍 Validation & Testing

```bash
# Check code quality (if pylint available)
pylint agents/ services/ app.py

# Run with test stock
python app.py --stock VNM --rounds 2 --output test_results.json

# Validate JSON output
python -m json.tool test_results.json

# Check database persistence
psql -h localhost -U debate_user -d debate_poc -c "SELECT * FROM debate_logs LIMIT 1;"
```

---

## 🐛 Troubleshooting

### Issue: GEMINI_API_KEY not found
**Solution**: Set environment variable
```bash
export GEMINI_API_KEY="your-actual-key"
```

### Issue: No data fetched (Demo mode active)
**Current**: If yfinance fails, uses demo data. To use real data:
```bash
pip install yfinance pandas pandas-ta
python app.py --stock VNM.VN  # Include .VN suffix for Vietnamese stocks
```

### Issue: Database connection error
**Solution**: Check PostgreSQL is running or disable DB:
```bash
# Disable DB (SQLite fallback)
unset DATABASE_URL
python app.py --stock VNM

# Or fix connection
docker-compose up postgres
export DATABASE_URL="postgresql://debate_user:debate_pass@localhost:5432/debate_poc"
```

### Issue: Gemini API rate limit
**Solution**: Built-in retry logic with exponential backoff. If persists:
- Wait 60s before next request
- Use smaller batch sizes
- Check API quota in Google Cloud Console

---

## 📝 Logs

Logs written to: `logs/debate.log`

**Typical flow**:
```
2025-11-06 10:15:42,123 | root | INFO | Gemini Multi-Agent Stock Debate PoC
2025-11-06 10:15:42,234 | services.gemini_service | INFO | Initialized GeminiService with model gemini-2.0-flash
2025-11-06 10:15:43,456 | services.debate_orchestrator | INFO | Starting debate on VNM (3 rounds, ...)
2025-11-06 10:15:44,567 | services.debate_orchestrator | INFO | Round 1: Debate and rebuttals
...
2025-11-06 10:16:12,890 | root | INFO | DEBATE COMPLETE ✓
```

---

## 🔐 Security & Production Notes

- ✅ API keys via environment variables (not hardcoded)
- ✅ Database credentials in `.env` (ignored by git)
- ✅ Connection pooling with `pool_recycle=3600`
- ✅ Retries with exponential backoff on transient failures
- ⚠️ **TODO for production**:
  - Add input validation (stock symbols)
  - Implement rate limiting
  - Add authentication for API endpoints
  - Use secrets manager for sensitive data
  - Add monitoring/alerting

---

## 📚 References

- **Microsoft Autogen**: [GitHub](https://github.com/microsoft/autogen)
- **Google Gemini API**: [Docs](https://ai.google.dev/)
- **SQLAlchemy ORM**: [Docs](https://sqlalchemy.org/)
- **Vietnamese Stock Market**: [HoSE](http://www.hose.vn/)

---

## 📄 License

MIT License - See LICENSE file

---

## 👤 Author

Gemini Multi-Agent Debate PoC - v4.0  
Built for minimal, production-ready autonomous financial analysis.

---

## ✨ Future Enhancements

- [ ] Real-time streaming debate output (WebSocket)
- [ ] Multi-stock portfolio analysis with agent disagreement tracking
- [ ] Fine-tuned models per agent expertise
- [ ] Integration with actual Vietnamese financial APIs
- [ ] Web dashboard for debate visualization
- [ ] Backtesting module: compare historical verdicts vs actual returns
- [ ] Agent consensus metrics & confidence calibration
