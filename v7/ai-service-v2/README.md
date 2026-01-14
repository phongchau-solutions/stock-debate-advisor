# Stock Debate Advisor v2 - Refactored AI Service

## Overview

Minimal, focused AI service implementing multi-agent debate for stock analysis. Agents analyze stocks using fundamental, technical, and sentiment data, with a Judge controlling debate rounds based on evidence quality and timeframe clarity.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment
```bash
export GEMINI_API_KEY="your-key-here"
```

Or create `.env`:
```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=4000
MIN_ROUNDS=1
MAX_ROUNDS=5
VERBOSE=false
DATA_STORE_PATH=/path/to/data_store/data/2026
```

### 3. Run API Server
```bash
uvicorn main:app --reload --port 8000
```

### 4. Run Demo UI (separate terminal)
```bash
streamlit run demo.py
```

Access at: http://localhost:8501

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Start Debate
```bash
curl -X POST http://localhost:8000/debate \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MBB",
    "timeframe": "3 months",
    "min_rounds": 1,
    "max_rounds": 5
  }'
```

## Architecture

- **engine.py**: DebateEngine + DataLoader - loads data from data_store, orchestrates agents and debate logic
- **main.py**: FastAPI server - REST API for debates
- **demo.py**: Streamlit UI - interactive demo
- **config.py**: Settings from environment + data_store validation
- **models.py**: Pydantic request/response schemas
- **constants.py**: Agent roles and v5-adapted system prompts

## Debate Flow

1. **Round N**: Each analyst (Fundamental, Technical, Sentiment) provides perspective for stated timeframe
2. **Judge Decision**: Evaluates evidence quality, timeframe alignment, novelty
3. **Continue or Conclude**: Judge decides based on:
   - Evidence: Concrete numbers vs vague claims
   - Alignment: Clear positions with timeframe context
   - Novelty: New insights vs repetition
   - Min/Max: Respects min_rounds, respects max_rounds
4. **Final Verdict**: When concluded, extracts recommendation, confidence, risks, monitor factors

## Data Source

Loads real stock data from `v7/data_store/data/2026/{TICKER}.VN/`:
- company_info.json
- financial_reports.json
- ohlc_prices.json

Supports Vietnamese stocks (MBB, ACB, BID, FPT, VCB, etc.)

## Design Principles

- **SOLID**: Single responsibility per module
- **DRY**: No duplicate code
- **KISS**: Minimal, straightforward implementation
- **Iterative**: Judge controls debate continuation, not fixed rounds
- **Timeframe-aware**: All agents and judge explicitly reference investment timeframe
- **V5-aligned**: System prompts adapted from v5 for consistency

