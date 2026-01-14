# V7 - Minimal CDK-Focused Demo App

Complete stock analysis platform with serverless backend, data service, AI service, and frontend.

## Architecture

```
v7/
├── ai-service-v2/          ⭐ Refactored AI engine (546 lines)
│   ├── config.py           Settings + validation
│   ├── constants.py        V5-adapted prompts
│   ├── models.py           Request/response schemas
│   ├── engine.py           DataLoader + DebateEngine (iterative)
│   ├── main.py             FastAPI endpoints
│   ├── demo.py             Streamlit UI
│   ├── QUICK_START.sh      One-command startup
│   ├── README.md
│   ├── REFACTORING.md
│   ├── TESTING.md
│   └── COMPLETION.md
│
├── data_store/             📊 Real stock data
│   ├── data/2026/
│   │   ├── MBB.VN/         Military Bank data
│   │   ├── ACB.VN/         Asia Commercial Bank data
│   │   ├── BID.VN/         BIDV data
│   │   └── ... 27 more Vietnamese stocks
│   └── lambda/             Lambda layer generators
│
├── frontend/               🎨 React UI (to connect)
│   ├── src/
│   ├── package.json
│   └── ... React app
│
├── cdk/                    ☁️ AWS CDK infrastructure (to build)
│   ├── lib/
│   ├── bin/
│   └── cdk.json
│
├── ai-service/             📦 Original ai-service (deprecate in favor of v2)
│
└── INDEX.md               This file

```

## Components

### 1. AI Service v2 (`ai-service-v2/`)
**Minimal, clean, production-ready**

- **What**: Multi-agent debate system for stock analysis
- **Agents**: Fundamental, Technical, Sentiment analysts + Judge
- **Data**: Real Vietnamese stock data from data_store
- **Debate**: Iterative with Judge controlling rounds based on evidence quality
- **Output**: Investment recommendation (BUY/SELL/HOLD) with timeframe-specific rationale
- **Tech**: FastAPI, CrewAI, Gemini LLM, Streamlit demo

```bash
# Quick start
cd ai-service-v2
conda activate chatbot_env
./QUICK_START.sh
```

### 2. Data Store (`data_store/`)
**Real stock data in JSON format**

- 30 Vietnamese stocks with 2026 data
- Per-stock structure: company_info.json, financial_reports.json, ohlc_prices.json
- Ready to feed into AI agents
- Expandable to more years/tickers

```bash
# Available tickers
ls data_store/data/2026/
```

### 3. Frontend (`frontend/`)
**To be implemented**

- React UI for stock debate interface
- Real-time debate streaming
- Results display with recommendations
- Portfolio builder from recommendations

### 4. CDK Infrastructure (`cdk/`)
**To be implemented**

- Lambda functions for API tier (wrapping FastAPI)
- DynamoDB for debate history
- S3 for data storage
- API Gateway for public endpoint
- VPC for security

## System Flow

```
User
  ↓
Frontend (React)
  ↓
API Gateway (CDK)
  ↓
Lambda (FastAPI wrapper)
  ↓
AI Service v2
  ├─ DataLoader → data_store
  ├─ DebateEngine
  │  ├─ Fundamental Agent
  │  ├─ Technical Agent
  │  ├─ Sentiment Agent
  │  └─ Judge Agent (controls debate)
  ↓
Response (Recommendation + Rationale)
  ↓
Frontend Display
```

## Key Features

### AI Service v2
✅ Real data from data_store (30 Vietnamese stocks)
✅ Iterative debate (min-max rounds controlled by Judge)
✅ Timeframe-aware analysis (1 month, 3 months, 6 months, 1 year)
✅ V5-aligned system prompts
✅ No hardcoded values
✅ Clean API/UI separation
✅ 546 lines of code (70% reduction from original)

### Data Store
✅ Company info (name, sector, market cap, description)
✅ Financial reports (P/E, ROE, ROA, revenue, margins, etc.)
✅ OHLC prices (daily data for technical analysis)
✅ Extensible JSON structure

### Frontend (Roadmap)
🔲 Stock ticker search
🔲 Real-time debate display
🔲 Investment recommendation cards
🔲 Portfolio builder
🔲 Trade alerts

### CDK Infrastructure (Roadmap)
🔲 Lambda deployment
🔲 DynamoDB persistence
🔲 API Gateway routing
🔲 Auto-scaling
🔲 CloudWatch monitoring

## Getting Started

### Option 1: Just AI Service v2 (Local Demo)
```bash
cd ai-service-v2
conda activate chatbot_env
./QUICK_START.sh
# Visit http://localhost:8501 for Streamlit demo
```

### Option 2: Full Stack (Frontend + API + CDK)
```bash
# 1. Start AI Service API
cd ai-service-v2
uvicorn main:app --reload --port 8000

# 2. Start Demo UI (separate terminal)
cd ai-service-v2
streamlit run demo.py

# 3. Build CDK (future)
cd cdk
cdk deploy
```

## API Endpoints

### Health Check
```bash
GET /health
→ {status: "healthy", version: "2.0"}
```

### Start Debate
```bash
POST /debate
{
  "ticker": "MBB",
  "timeframe": "3 months",
  "min_rounds": 1,
  "max_rounds": 5
}
→ {
  "ticker": "MBB",
  "timeframe": "3 months",
  "actual_rounds": 2,
  "rounds": [...],
  "final_recommendation": "BUY",
  "confidence": "High",
  "rationale": "...",
  "risks": "...",
  "monitor": "..."
}
```

## Supported Tickers

Vietnamese stocks in data_store (2026):
- Banks: MBB, ACB, BID, VCB, TPB, TCB, STB, SHB, HDB
- Energy: GAS, POW
- Real Estate: BVH, VHM, KDH, PDR, NVL
- Retail: MWG, SAB
- Technology: FPT, SSI
- Others: BCM, CTG, GVR, HPG, MSN, PLX, VIB, VIC, VJC, SSB

## Configuration

### Environment Variables
```
GEMINI_API_KEY          (Required) Google Gemini API key
GEMINI_MODEL            (Default: gemini-1.5-flash)
TEMPERATURE             (Default: 0.7)
MAX_TOKENS              (Default: 4000)
MIN_ROUNDS              (Default: 1)
MAX_ROUNDS              (Default: 5)
DATA_STORE_PATH         (Default: v7/data_store/data/2026)
VERBOSE                 (Default: false)
```

### .env File
```
GEMINI_API_KEY=sk-...
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=4000
MIN_ROUNDS=1
MAX_ROUNDS=5
DATA_STORE_PATH=/home/npc11/work/stock-debate-advisor/v7/data_store/data/2026
VERBOSE=false
```

## Principles

- **SOLID**: Single responsibility per module
- **DRY**: No code duplication
- **KISS**: Minimal, straightforward implementation
- **Timeframe-Aware**: All agents explicit about investment horizon
- **Evidence-Based**: Judge controls debate quality, not fixed rounds
- **No Magic Numbers**: All configuration driven
- **Production-Ready**: Error handling, validation, logging

## Next Steps

1. **Test AI Service v2** locally with demo data
2. **Connect Frontend** to ai-service-v2 API endpoints
3. **Build CDK Infrastructure** for AWS deployment
4. **Add Data Updates** for more stocks/years
5. **Implement Caching** for better performance
6. **Add Streaming** for real-time debate display

## Documentation

- `ai-service-v2/README.md` - API documentation
- `ai-service-v2/REFACTORING.md` - Before/after analysis
- `ai-service-v2/TESTING.md` - Testing guide
- `ai-service-v2/COMPLETION.md` - Detailed summary
- `ai-service-v2/QUICK_START.sh` - One-command startup

## Contact & Support

For issues with:
- **AI Service**: See `ai-service-v2/TESTING.md`
- **Data**: Check `data_store/` structure
- **API**: Test with curl examples in `ai-service-v2/README.md`
- **Deployment**: Will be documented in CDK section

---

**Status**: ✅ AI Service v2 Complete | 🔲 Frontend Roadmap | 🔲 CDK Roadmap
**Last Updated**: 2026-01-15
