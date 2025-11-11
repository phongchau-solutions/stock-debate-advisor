# Stock Debate Advisor V5 - Architecture

Technical architecture for the multi-agent debate system.

## System Overview

Multi-agent debate platform where specialized analyst agents discuss Vietnamese stock analysis under a Moderator's guidance, evaluated by a Judge to produce consensus recommendations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│              (Real-time Streaming Interface)             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│               Debate Orchestrator                        │
│         (Manages rounds, memory, flow control)           │
└───┬──────────┬──────────┬──────────┬──────────┬─────────┘
    │          │          │          │          │
┌───▼────┐ ┌──▼──────┐ ┌─▼────────┐ ┌▼────────┐ ┌▼──────┐
│Fundmtl │ │Technical│ │Sentiment │ │Moderator│ │ Judge │
│ Agent  │ │  Agent  │ │  Agent   │ │  Agent  │ │ Agent │
└───┬────┘ └──┬──────┘ └─┬────────┘ └┬────────┘ └┬──────┘
    │         │          │           │          │
    └─────────┴──────────┴───────────┴──────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                 Data Loader                              │
│       (Loads financial, OHLC, news data)                 │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Google Gemini API                           │
│            (gemini-1.5-flash LLM)                        │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer (Streamlit UI)

**Purpose**: User interface for debate interaction

**Features**:
- Stock symbol selection
- Real-time debate streaming
- Memory visualization
- Round counter
- Final verdict display

**Technology**: Streamlit with SSE (Server-Sent Events)

### 2. Orchestration Layer

**Purpose**: Coordinates multi-agent debate flow

**Components**:
- `DebateOrchestrator` - Main orchestration logic
- Memory management - Tracks conversation history
- Round control - Manages debate progression
- Critique detection - Identifies agent rebuttals

**Flow**:
1. Initialize agents with stock data
2. Execute rounds (analysis → critiques)
3. Judge evaluation after each round
4. Continue or conclude based on quality
5. Final verdict generation

### 3. Agent Layer

### 3. Agent Layer

Five specialized agents with distinct roles:

#### Fundamental Agent
- **Data**: Financial statements, metrics (PE, ROE, debt)
- **Analysis**: Valuation, growth potential, financial health
- **Output**: BUY/HOLD/SELL with financial reasoning

#### Technical Agent
- **Data**: OHLC prices, volumes, technical indicators
- **Analysis**: Trends, support/resistance, momentum
- **Output**: BUY/HOLD/SELL with technical reasoning

#### Sentiment Agent
- **Data**: Vietnamese news articles, market sentiment
- **Analysis**: News tone, market mood, public perception
- **Output**: BUY/HOLD/SELL with sentiment reasoning

#### Moderator Agent
- **Role**: Debate coordinator
- **Functions**: Opens rounds, manages flow, detects critiques
- **Output**: Contextual prompts for each round

#### Judge Agent
- **Role**: Quality evaluator
- **Functions**: Assesses debate quality, decides continuation
- **Output**: Final BUY/HOLD/SELL verdict with synthesis

### 4. Data Layer

**Data Loader** (`data_loader.py`):
- Loads CSV files from `data/finance/` and `data/news/`
- Formats data for agent consumption
- Handles missing data gracefully

**Data Structure**:
```
data/
├── finance/
│   ├── {SYMBOL}_financials.csv  # Balance sheet, income, cash flow
│   └── {SYMBOL}_ohlc.csv        # Price data, technical indicators
└── news/
    └── {SYMBOL}_news.csv        # News articles, titles, content
```

### 5. LLM Integration

**Google Gemini API**:
- Model: `gemini-1.5-flash` (fast, cost-effective)
- Temperature: 0.7 (balanced creativity/consistency)
- Streaming: Enabled for real-time UI updates

**Agent Implementation**:
- Each agent extends `BaseAgent` class
- System prompts loaded from `prompts/` directory
- Conversation memory tracked per agent
- Context window managed automatically

## Debate Flow

### Round Structure

1. **Round N (Analysis)**:
   - Moderator opens with context
   - Each analyst presents analysis
   - Agents propose BUY/HOLD/SELL

2. **Round N+1 (Critique)**:
   - Agents review peer analyses
   - Respond to conflicting viewpoints
   - Refine or maintain positions

3. **Judge Evaluation**:
   - Assesses discussion quality
   - Checks for consensus
   - Decides: CONTINUE or CONCLUDE

4. **Conclusion**:
   - Judge synthesizes all viewpoints
   - Produces final BUY/HOLD/SELL
   - Provides comprehensive rationale

### Memory Management

Each agent maintains:
- **Conversation History**: All previous statements
- **Critique Tracking**: Who critiqued whom
- **Position Evolution**: How stance changed over rounds

Prevents:
- Repetitive arguments
- Circular discussions
- Loss of context

## Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| LLM | Google Gemini API |
| UI Framework | Streamlit |
| Data Format | CSV (Pandas) |
| Config | python-dotenv |
| Container | Docker + Docker Compose |

## Deployment

### Docker Deployment

```bash
# Build and run
docker compose up --build

# Access at http://localhost:8501
```

### Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with GEMINI_API_KEY

# Run
streamlit run app.py
```

## Configuration

Environment variables (`.env`):

```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
FINANCE_DATA_PATH=./data/finance
NEWS_DATA_PATH=./data/news
MIN_ROUNDS=2
MAX_ROUNDS=10
```

## Extensibility

### Adding New Agents

```python
from agents import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self, stock_data):
        super().__init__(
            name="New Agent",
            role="new_analyst",
            system_prompt=load_prompt("new_agent.txt")
        )
        self.data = stock_data
    
    def generate_response(self, context):
        # Custom logic here
        return self.call_llm(context)
```

### Modifying Debate Logic

Edit `orchestrator.py`:
- Change round limits
- Adjust critique detection
- Modify continuation criteria
- Add new debate phases

### Customizing Prompts

Edit files in `prompts/`:
- `fundamental_agent.txt` - Financial analysis instructions
- `technical_agent.txt` - Technical analysis instructions
- `sentiment_agent.txt` - Sentiment analysis instructions
- `moderator_agent.txt` - Moderation instructions
- `judge_agent.txt` - Judging criteria

## Performance Considerations

**Optimization Strategies**:
- Parallel agent execution (where possible)
- Response streaming for better UX
- Caching repeated data loads
- Efficient memory management

**Scalability**:
- Stateless agent design
- Horizontal scaling possible
- Multiple debate instances
- Load balancing ready

## Security

**Best Practices**:
- API keys in `.env` (not committed)
- Read-only data mounts in Docker
- Non-root user in container
- Health checks enabled

## Monitoring

**Health Checks**:
- Streamlit health endpoint
- Container restart policies
- Log aggregation in `logs/`

**Metrics to Track**:
- Response times per agent
- Debate completion rates
- API usage and costs
- Error rates

---

**Architecture Version**: 5.0  
**Last Updated**: November 2025  
**Status**: Production Demo
