## Testing ai-service-v2

### Verify Structure
```bash
cd /home/npc11/work/stock-debate-advisor/v7/ai-service-v2
ls -la
```

### Install & Test
```bash
# Activate environment
conda activate chatbot_env

# Install dependencies
pip install -q -r requirements.txt

# Verify imports
python -c "from main import app; from engine import DebateEngine; print('✅ Imports OK')"

# Check data_store
python -c "from engine import DataLoader; dl = DataLoader(); print('✅ DataLoader OK')"
```

### Run API Server
```bash
cd /home/npc11/work/stock-debate-advisor/v7/ai-service-v2
conda activate chatbot_env
uvicorn main:app --reload --port 8000
```

### Test Endpoints (separate terminal)
```bash
# Health check
curl http://localhost:8000/health

# Start debate (MBB is available in data_store)
curl -X POST http://localhost:8000/debate \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MBB",
    "timeframe": "3 months",
    "min_rounds": 1,
    "max_rounds": 3
  }'
```

### Run Streamlit Demo (third terminal)
```bash
cd /home/npc11/work/stock-debate-advisor/v7/ai-service-v2
conda activate chatbot_env
streamlit run demo.py
```

Browse to http://localhost:8501 and test with available tickers:
- MBB, ACB, BID, VCB, FPT, CTG, HPG, BVH, etc. (all in data_store)

### Available Tickers
```bash
ls /home/npc11/work/stock-debate-advisor/v7/data_store/data/2026/
```

All tickers follow pattern: `{SYMBOL}.VN/`

### Debug Environment
```bash
conda activate chatbot_env
python -c "
from config import settings
print(f'DATA_STORE_PATH: {settings.DATA_STORE_PATH}')
print(f'Exists: {settings.DATA_STORE_PATH.exists()}')
print(f'GEMINI_API_KEY: {settings.GEMINI_API_KEY[:10]}...')
"
```

### Expected Behavior
1. API receives debate request with ticker, timeframe, min/max rounds
2. DataLoader fetches stock data from data_store
3. Round 1: Each analyst provides perspective for timeframe
4. Judge evaluates evidence quality, timeframe clarity, novelty
5. Judge decides: CONTINUE (if min < current < max) or CONCLUDE
6. Repeat until CONCLUDE or max_rounds
7. Final verdict extracted from last judge decision
8. Response includes all rounds + final verdict with recommendation, confidence, risks, monitor

### Common Errors
- `GEMINI_API_KEY not set`: Set in .env or export
- `Data store path not found`: Check DATA_STORE_PATH in .env
- `No data found for {TICKER}`: Ticker not in data_store (use ls to check available)
- Connection refused on port 8000: API server not running
