# AI Service - Multi-Agent Debate Orchestration

CrewAI-based service for orchestrating multi-agent stock debate. Implements specialized agents (Fundamental, Technical, Sentiment analysts) plus Moderator and Judge for structured investment analysis.

## Features

- **CrewAI Framework**: Agent-based orchestration for collaborative multi-agent systems
- **Agent Roles**:
  - Fundamental Analyst: Financial statement analysis, ratios, valuation metrics
  - Technical Analyst: Price trends, indicators (RSI, MACD, MA), chart patterns
  - Sentiment Analyst: News sentiment analysis, market psychology, themes
  - Moderator: Guides debate, challenges arguments, ensures balance
  - Judge: Evaluates arguments and provides final investment recommendation
- **Multi-Agent Debate**: Structured debate format with reasoning and consensus building
- **Session Management**: Conversation state and memory management
- **Tools Integration**: Access to data service for financial information
- **Streamlit Demo**: Interactive web UI for agent interaction
- **API Endpoints**: REST API for debate orchestration

## Running

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start Streamlit demo UI
streamlit run demo_app.py
# Opens at http://localhost:8501

# Start API server
python api_server.py
# API available at http://localhost:8000
```

### Docker

```bash
# Build image
docker build -t ai-service .

# Run container
docker run -p 8501:8501 -p 8000:8000 --env-file .env ai-service
```

## Configuration

Set environment variables in `.env`:

```bash
# LLM Configuration
GEMINI_API_KEY=your_api_key
LLM_MODEL=gemini-1.5-pro
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
