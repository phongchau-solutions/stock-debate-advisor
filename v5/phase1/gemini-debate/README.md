# Gemini Multi-Agent Stock Debate System

A production-ready multi-agent debate system using Google Gemini API for Vietnamese stock analysis with conversation memory.

## 🎯 Overview

This system orchestrates three AI agents (Fundamental, Technical, and Sentiment analysts) with a Moderator and Judge in a structured debate to produce BUY/HOLD/SELL recommendations for Vietnamese stocks.

### Key Features

- **Conversation Memory**: Agents track previous statements to avoid repetition
- **Dynamic Debate Rounds**: Quality-based continuation (not fixed rounds)
- **Real-time Streaming**: Live debate updates in Streamlit UI
- **Critique Detection**: Automatic identification and response to agent critiques
- **Role Separation**: Moderator coordinates, Judge assesses quality

### Architecture

- **Environment**: Python 3.11+
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **UI**: Streamlit with real-time streaming
- **Container**: Docker support with docker-compose

## 🧩 Agents

| Agent | Role | Data Source | Memory |
|-------|------|-------------|--------|
| **Fundamental Agent** | Analyzes financial statements, metrics (PE, ROE, debt) | `/v5/data/finance` | ✅ |
| **Technical Agent** | Analyzes OHLC, price patterns, technical levels | `/v5/data/finance` | ✅ |
| **Sentiment Agent** | Assesses tone from Vietnamese news articles | `/v5/data/news` | ✅ |
| **Moderator Agent** | Coordinates debate flow, detects critiques | System orchestrator | ✅ |
| **Judge Agent** | Evaluates quality, decides continuation, makes final verdict | Synthesized output | ✅ |

## 🔁 Debate Flow

1. **Initialization**: Memory reset, stock symbol selected
2. **Round Opening**: Moderator opens with context-aware prompt
3. **Agent Analysis**: Each agent analyzes with memory + debate context
4. **Critique Detection**: System detects and routes rebuttals
5. **Judge Commentary**: Quality assessment after each round
6. **Continuation Check**: Judge decides CONTINUE or CONCLUDE based on quality
7. **Final Verdict**: Judge produces BUY/HOLD/SELL with rationale

## 📋 Prerequisites

- Python 3.11+
- Google Gemini API key
- Vietnamese stock data in `/v5/data/finance` and `/v5/data/news`

## 🚀 Quick Start

### Local Setup

1. **Clone and navigate to the project**:
```bash
cd /path/to/v5/phase1/gemini-debate
```

2. **Create environment**:
```bash
# Using conda (recommended)
conda env create -f environment.yml
conda activate gemini-debate

# Or using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Run the application**:
```bash
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

### Docker Setup

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

2. **Or build manually**:
```bash
docker build -t gemini-debate .
docker run -p 8501:8501 --env-file .env -v $(pwd)/../../data:/app/data gemini-debate
```

## 📁 Project Structure

```
gemini-debate/
├── app.py                      # Streamlit UI with real-time streaming
├── orchestrator.py             # Debate orchestrator with memory management
├── agents.py                   # Agent implementations with conversation memory
├── data_loader.py              # Data loading utilities
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── environment.yml             # Conda environment specification
├── setup.sh                    # Environment setup script
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── prompts/                    # System prompts for agents
│   ├── fundamental_agent.txt
│   ├── technical_agent.txt
│   ├── sentiment_agent.txt
│   ├── moderator_agent.txt
│   └── judge_agent.txt
├── examples/                   # Example scripts and tests
│   ├── example_debate.py       # Simple programmatic example
│   ├── quick_test.py          # System validation test
│   └── test_system.py         # Comprehensive system test
└── utils/                      # Utility scripts
    ├── convert_data.py         # Data format conversion
    ├── convert_financials_to_json.py
    ├── extract_field_mapping.py
    └── field_mapping.json
```

## 📊 Data Format

### Financial Data
Expected in `../../data/finance/`:
- `{SYMBOL}_financials.csv` - Balance sheet, income statement, cash flow
- `{SYMBOL}_ohlc.csv` - OHLC price data with technical indicators

### News Data
Expected in `../../data/news/`:
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
FINANCE_DATA_PATH=../../data/finance
NEWS_DATA_PATH=../../data/news
VCI_DATA_PATH=../../data/vci

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
