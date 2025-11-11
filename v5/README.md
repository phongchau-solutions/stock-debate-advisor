# Stock Debate Advisor - V5

Multi-agent AI debate system for Vietnamese stock analysis using Google Gemini API. Orchestrates specialized analyst agents in structured debates to produce data-driven BUY/HOLD/SELL recommendations.

## 🎯 Overview

Three AI agents (Fundamental, Technical, and Sentiment) debate stock analysis under a Moderator's guidance, evaluated by a Judge agent to reach consensus recommendations.

### Key Features

✅ **Multi-Agent Debate**: Specialized agents with distinct analytical perspectives  
✅ **Conversation Memory**: Agents track discussion history to build on insights  
✅ **Dynamic Rounds**: Quality-driven continuation until consensus  
✅ **Real-time Streaming**: Live debate updates via Streamlit  
✅ **Vietnamese Market**: Optimized for Vietnamese stock data and news

### Technology Stack

- **Python**: 3.11+
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **Framework**: Google Generative AI
- **UI**: Streamlit with streaming
- **Deploy**: Docker + Docker Compose

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Docker & Docker Compose installed
- Google Gemini API key ([Get one free](https://ai.google.dev/))
- Stock data files in `data/` directory

### Run the Demo

```bash
# 1. Clone the repository
git clone <repository-url>
cd stock-debate-advisor/v5

# 2. Set your API key
cp .env.example .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# 3. Start the application
docker compose up

# 4. Open browser
# Navigate to: http://localhost:8501
```

That's it! The debate system is now running.

### Alternative: Local Setup (Without Docker)

```bash
# 1. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Run application
streamlit run app.py
```

## 🧩 Agent System

| Agent | Role | Data Source |
|-------|------|-------------|
| **Fundamental** | Financial metrics (PE, ROE, debt, growth) | `data/finance/` |
| **Technical** | OHLC patterns, indicators, trends | `data/finance/` |
| **Sentiment** | Vietnamese news analysis, market mood | `data/news/` |
| **Moderator** | Coordinates debate flow, manages critiques | - |
| **Judge** | Evaluates quality, makes final BUY/HOLD/SELL | - |

## 🔁 How It Works

1. **Initialize**: Select stock symbol, load data
2. **Round 1-N**: Each analyst presents analysis with memory
3. **Critique Phase**: Agents respond to each other's points
4. **Judge Assessment**: Quality check after each round
5. **Decision**: Continue debate or conclude with verdict
6. **Final Output**: Structured BUY/HOLD/SELL recommendation

## 📁 Project Structure

```
v5/
├── app.py                 # Streamlit UI with real-time streaming
├── orchestrator.py        # Debate orchestrator with memory
├── agents.py              # Agent implementations
├── data_loader.py         # Data loading utilities
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── ARCHITECTURE.md       # Technical architecture
├── QUICKSTART.md         # 5-minute guide
├── prompts/              # Agent system prompts
│   ├── fundamental_agent.txt
│   ├── technical_agent.txt
│   ├── sentiment_agent.txt
│   ├── moderator_agent.txt
│   └── judge_agent.txt
└── data/                 # Stock and news data
    ├── finance/          # Financial data CSV files
    └── news/             # News articles CSV files
```

## 📊 Data Format

### Financial Data (`data/finance/`)

- `{SYMBOL}_financials.csv` - Balance sheet, income statement, cash flow
- `{SYMBOL}_ohlc.csv` - OHLC price data with technical indicators

### News Data (`data/news/`)

- `{SYMBOL}_news.csv` - News articles with titles and content
- `{SYMBOL}_sentiment.csv` - Sentiment scores (optional)

## 🎨 UI Features

- **Stock Selection**: Dropdown with available symbols
- **Real-time Streaming**: Live debate updates
- **Memory Indicators**: Agent conversation history
- **Critique Highlighting**: Visual rebuttals
- **Round Counter**: Dynamic rounds based on quality
- **Judge Commentary**: After-round assessments
- **Final Verdict**: BUY/HOLD/SELL with rationale
- **Transcript Export**: Download debate history

## 🔧 Configuration

Edit `.env` to configure:

```bash
# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7

# Data paths
FINANCE_DATA_PATH=./data/finance
NEWS_DATA_PATH=./data/news

# Debate settings
MIN_ROUNDS=2              # Minimum rounds before conclusion
MAX_ROUNDS=10             # Maximum debate rounds
```

## 🐛 Troubleshooting

**API Key Not Set**
```bash
# Solution: Add your key to .env
echo "GEMINI_API_KEY=your_key_here" >> .env
```

**No Data Found**
```bash
# Solution: Check data directory structure
ls -la data/finance/
ls -la data/news/
```

**Port Already in Use**
```bash
# Solution: Change port in docker-compose.yml or use:
docker compose down
# Then restart
```

## 📄 License

Proof-of-concept for demonstration purposes.

## 🤝 Contributing

For production deployment, consider:

- Error handling & retry logic
- Rate limiting for API calls
- Caching for responses
- Enhanced data validation
- Unit & integration tests
- Performance monitoring

---

**Version**: 5.0  
**Status**: Production Demo  
**Framework**: Google Gemini API  
**Last Updated**: November 2025
````

## 📊 Data Format

### Financial Data
Expected in `data/finance/`:
- `{SYMBOL}_financials.csv` - Balance sheet, income statement, cash flow
- `{SYMBOL}_ohlc.csv` - OHLC price data with technical indicators

### News Data
Expected in `data/news/`:
- `{SYMBOL}_news.csv` - News articles with titles and content
- `{SYMBOL}_sentiment.csv` - Sentiment analysis results

## 🎨 UI Features

The Streamlit interface provides:
- **Stock Selection**: Dropdown with available symbols
- **Real-time Streaming**: Live debate updates as agents respond
- **Memory Indicators**: Shows agent conversation history
- **Critique Highlighting**: Visual indicators for agent rebuttals
- **Round Counter**: Dynamic rounds based on debate quality
- **Judge Commentary**: After-round quality assessments
- **Final Verdict**: Structured BUY/HOLD/SELL recommendation
- **Transcript Export**: Download full debate history

## 🔧 Configuration

Edit `.env` to configure:

```bash
# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=2048

# Data paths (relative to project root)
FINANCE_DATA_PATH=data/finance
NEWS_DATA_PATH=data/news
VCI_DATA_PATH=../data/vci

# Debate settings
DEBATE_ROUNDS=10                # Minimum rounds before judge can conclude
AGENTS_PER_ROUND=3
```

## 🧪 Testing

### Run Example Debate

```bash
python examples/example_debate.py
```

### Quick System Validation

```bash
python examples/quick_test.py
```

### Test Individual Components

```python
from orchestrator import DebateOrchestrator

# Run debate
result = orch.run_full_debate("VNM", "3 months")

# Export transcript
orch.export_transcript("debate_transcript.json")
```

## 📝 Development Notes

### Agent Design
- Each agent loads its system prompt from `prompts/` directory
- Agents use Gemini API for natural language generation
- Data is formatted specifically for each agent's expertise

### Debate Orchestration
- Uses round-based conversation flow
- Context is maintained across rounds
- Moderator advances conversation between rounds
- Judge synthesizes final verdict after all rounds

### Extensibility
- Add new agents by extending `BaseAgent` class
- Modify system prompts to adjust agent behavior
- Configure debate rounds via environment variables
- Extend data loaders for additional data sources

## 🐛 Troubleshooting

**Issue**: "GEMINI_API_KEY is not set"
- Solution: Copy `.env.example` to `.env` and add your API key

**Issue**: "Finance data path does not exist"
- Solution: Ensure `/v5/data/finance` directory exists with CSV files

**Issue**: Agents produce generic responses
- Solution: Check that data files are properly formatted and contain valid data

## 📄 License

This is a proof-of-concept project for demonstration purposes.

## 🤝 Contributing

This is a minimal PoC. For production use, consider:
- Error handling and retry logic
- Caching for API calls
- Rate limiting
- Enhanced data validation
- Unit tests
- Performance optimization

## 📧 Contact

For questions or issues, please open a GitHub issue.
