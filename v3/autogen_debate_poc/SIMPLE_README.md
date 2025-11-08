# Simplified Multi-Agent Stock Analysis System

## Overview
Clean, working multi-agent system for Vietnamese stock market analysis without complex AutoGen dependencies.

## Architecture

```
simple_app.py (all-in-one)
├── SimpleAgent (base class)
├── TechnicalAgent (RSI, MA indicators)
├── FundamentalAgent (P/E, ROE, P/B ratios)
├── SentimentAgent (news keyword analysis)
└── DebateOrchestrator (coordinates debate)
```

## Features
✅ **3 Specialized Agents**: Technical, Fundamental, Sentiment  
✅ **Multi-Round Debate**: Agents analyze and reach consensus  
✅ **Early Termination**: Stops when all agents agree  
✅ **Real-Time UI**: Streamlit with live updates  
✅ **Data Caching**: SQLite cache for faster demos  
✅ **No Complex Dependencies**: Pure Python, no AutoGen complexity  

## Quick Start

### 1. Install Dependencies
```bash
pip install streamlit pandas numpy sqlalchemy yfinance beautifulsoup4 requests aiohttp
```

### 2. Run the App
```bash
streamlit run simple_app.py
```

### 3. Analyze Stocks
- Enter stock symbol (e.g., VNM, VIC, VCB)
- Set analysis period and minimum rounds
- Click "Start Analysis"
- Watch agents debate and reach consensus

## How It Works

### Data Flow
1. **Fetch Data** → StockDataService gets OHLCV, financials, news
2. **Agent Analysis** → Each agent analyzes independently
3. **Multi-Round Debate** → Agents present findings each round
4. **Consensus** → Weighted voting based on confidence
5. **Final Decision** → BUY/SELL/HOLD recommendation

### Agent Logic

**Technical Agent**
- RSI (14-period)
- Moving Averages (5-day, 20-day)
- Signal: Buy if oversold + uptrend, Sell if overbought + downtrend

**Fundamental Agent**
- P/E Ratio (valuation)
- ROE (profitability)
- P/B Ratio (book value)
- Signal: Buy if undervalued + strong ROE, Sell if overvalued

**Sentiment Agent**
- News keyword analysis
- Positive/negative word counting
- Signal: Buy if positive sentiment, Sell if negative

### Consensus Algorithm
```python
# Weighted voting by confidence
for signal, confidence in agent_outputs:
    votes[signal] += confidence

final_decision = signal_with_highest_vote
```

## Data Sources

### Primary: Vietcap API (via ref/zstock)
- OHLCV data
- Financial ratios
- Company information
- **Status**: Currently blocked (403)

### Fallback: YFinance
- Historical prices (.VN suffix)
- Basic company data
- **Status**: Working but limited for Vietnamese stocks

### Last Resort: Synthetic Data
- Realistic price movements
- Simulated financial ratios
- Demo news articles
- **Purpose**: Reliable demos when APIs fail

## File Structure

```
v3/autogen_debate_poc/
├── simple_app.py              # Main application (all-in-one)
├── services/
│   ├── stock_data_service.py  # Data fetching with cache
│   ├── database.py            # SQLAlchemy models
│   └── data_cache_service.py  # Cache operations
├── adapters/
│   ├── base_adapter.py        # Adapter interface
│   ├── vietcap_adapter.py     # Vietcap API (blocked)
│   └── yfinance_adapter.py    # YFinance fallback
└── requirements.txt           # Python dependencies
```

## Configuration

### Cache Settings
```python
# In simple_app.py
data_service = StockDataService(
    use_cache=True,           # Enable caching
    cache_max_age_hours=24    # 24-hour TTL
)
```

### Debate Parameters
- **min_rounds**: Minimum debate rounds (default: 2)
- **period_days**: Historical data period (default: 30)
- **Early termination**: Enabled when all agents agree

## Extending the System

### Add New Agent
```python
class NewAgent(SimpleAgent):
    def __init__(self):
        super().__init__("New Analyst", "New Analysis Type")
    
    def analyze(self, stock_symbol: str, data: dict) -> dict:
        # Your analysis logic
        return {
            'agent': self.name,
            'signal': 'buy|sell|hold',
            'confidence': 0.0-1.0,
            'rationale': 'Explanation...'
        }

# Register in orchestrator
orchestrator.agents.append(NewAgent())
```

### Customize Indicators
Edit the agent classes in `simple_app.py`:
- `TechnicalAgent.analyze()` - Add MACD, Bollinger Bands, etc.
- `FundamentalAgent.analyze()` - Add Debt/Equity, Current Ratio, etc.
- `SentimentAgent.analyze()` - Add NLP models, API sentiment, etc.

## Troubleshooting

### No Data Returned
- Check internet connection
- Vietcap API may be blocked (expected)
- System will fall back to synthetic data automatically

### SQLite Errors
```bash
rm stock_debate.db  # Delete old database
python simple_app.py  # Will create fresh database
```

### Import Errors
```bash
pip install -r requirements.txt
```

## Future Enhancements

### Phase 1 (Current)
- ✅ Rule-based agents
- ✅ Simple consensus
- ✅ Streamlit UI
- ✅ Data caching

### Phase 2 (Optional)
- 🔄 LLM-powered agents (OpenAI, Gemini)
- 🔄 Advanced NLP sentiment
- 🔄 Portfolio optimization
- 🔄 Real-time WebSocket data

### Phase 3 (Future)
- 📋 Historical backtesting
- 📋 Multi-stock comparison
- 📋 Risk assessment
- 📋 Alert notifications

## Why This Approach?

### Pros
✅ **Simple**: Single file, easy to understand  
✅ **Working**: No dependency conflicts  
✅ **Fast**: Rule-based agents respond instantly  
✅ **Reliable**: Fallback data sources  
✅ **Extensible**: Easy to add features  

### Trade-offs
⚠️ **No Real LLM**: Agents use rules, not language models  
⚠️ **Basic Logic**: Simple indicator thresholds  
⚠️ **No Learning**: Agents don't improve over time  

For a PoC/demo, this is the right balance of simplicity and functionality.

## License
MIT License - Feel free to use and modify

## Support
For issues or questions, check:
1. This README
2. Code comments in `simple_app.py`
3. Services documentation in `/services/`
