# Autogen Multi-Agent Financial Debate POC

## Vietnamese Stock Market Investment Decisioning

This is a production-lean proof-of-concept demonstrating Microsoft Autogen orchestrating multi-agent debates for Vietnamese stock analysis using Gemini, Vietcap API, and Streamlit visualization.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key
- (Optional) Vietcap API key

### 1. Clone and Setup
```bash
# Navigate to the project directory
cd autogen_debate_poc

# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or your preferred editor
```

### 2. Run with Docker Compose
```bash
# Build and start the application
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access the Application
Open your browser and navigate to: http://localhost:8501

## 🏗️ Architecture

### Multi-Agent System
- **Technical Agent**: Analyzes price trends, volume, and technical indicators
- **Fundamental Agent**: Evaluates financial ratios, earnings, and valuation  
- **Sentiment Agent**: Analyzes news sentiment from VnEconomy and WSJ
- **Debate Orchestrator**: Manages multi-agent debate using Autogen

### Technology Stack
- **Core Orchestration**: Microsoft Autogen
- **Reasoning LLM**: Google Gemini API
- **UI/Display**: Streamlit
- **Data Sources**: Vietcap API, VnEconomy, WSJ (with demo fallbacks)
- **Containerization**: Docker

## 📊 Features

### Real-Time Debate Visualization
- Live chat-like interface showing agent discussions
- Round-by-round progress tracking
- Individual agent analysis displays
- Interactive charts and metrics

### Comprehensive Analysis
- Technical indicators (RSI, MACD, moving averages)
- Fundamental metrics (P/E, P/B, ROE, debt ratios)
- Sentiment analysis from Vietnamese and international news
- Risk assessment and confidence scoring

### Export Capabilities
- Download debate transcript as .txt
- Export full results as JSON
- Shareable analysis reports

## 🎯 Usage Example

### Input
- **Stock**: VNM (Vinamilk)
- **Period**: 30 days

### System Action
1. Retrieves OHLCV data and financial metrics
2. Crawls news from VnEconomy and WSJ
3. Initializes 3 specialized agents
4. Conducts 5-round structured debate
5. Reaches consensus on BUY/HOLD/SELL decision

### Output
- Final recommendation with confidence score
- Detailed rationale with supporting evidence
- Risk assessment and key factors
- Complete debate transcript
- Visual analysis dashboard

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
VIETCAP_API_KEY=your_vietcap_api_key_here
DEFAULT_MAX_ROUNDS=5
USE_DEMO_DATA=true
```

### Supported Vietnamese Stocks
- VNM (Vinamilk)
- VIC (Vingroup) 
- VCB (Vietcombank)
- FPT (FPT Corporation)
- GAS (PetroVietnam Gas)
- And many more...

## 🐳 Docker Commands

### Development
```bash
# Build only
docker-compose build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker-compose down -v --rmi all
```

### Production
```bash
# Run in production mode
docker-compose -f docker-compose.yml up -d

# Scale if needed (not applicable for this single-service app)
# docker-compose scale autogen-debate-poc=2
```

## 📁 Project Structure

```
autogen_debate_poc/
├── agents/
│   ├── __init__.py           # Base agent classes
│   ├── technical_agent.py    # Technical analysis agent
│   ├── fundamental_agent.py  # Fundamental analysis agent
│   └── sentiment_agent.py    # Sentiment analysis agent
├── data/
│   └── data_integration.py   # Data fetching and integration
├── logs/                     # Application logs
├── app.py                    # Streamlit frontend
├── debate_orchestrator.py    # Autogen orchestration logic
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
├── .env.example            # Environment template
└── README.md               # This file
```

## 🧪 Testing

### Test with VNM Stock
1. Start the application
2. Enter "VNM" as stock symbol
3. Select "30 days" period
4. Click "Start Debate"
5. Observe real-time multi-agent discussion
6. Review final BUY/HOLD/SELL recommendation

### Expected Output
- Interactive debate between 3 agents
- Technical analysis showing trend indicators
- Fundamental valuation assessment
- Vietnamese market sentiment analysis
- Clear investment recommendation with rationale

## 🔍 Data Sources

### Stock Data
- **Primary**: Vietcap API (when available)
- **Fallback**: Yahoo Finance with .VN suffix
- **Demo**: Realistic simulated OHLCV data

### News Sources
- **VnEconomy**: Vietnamese financial news
- **Wall Street Journal**: International market coverage
- **Demo Mode**: Realistic Vietnamese stock news templates

## ⚠️ Important Notes

### Demo Mode
- Application includes comprehensive demo data
- Works without real API connections
- Suitable for testing and demonstration

### API Requirements
- **Gemini API**: Required for LLM reasoning
- **Vietcap API**: Optional, falls back to demo data
- **News APIs**: Currently using demo data

### Performance
- Debate typically takes 2-5 minutes
- Results depend on API response times
- Cached data improves subsequent runs

## 🚀 Future Enhancements

### Planned Improvements
- Milvus integration for semantic retrieval (RAG)
- Airflow DAGs for periodic data ingestion
- Prometheus + OpenTelemetry observability
- Multi-market comparison capabilities
- Advanced portfolio optimization

### Production Readiness
- Real Vietcap API integration
- Professional news API connections
- Enhanced error handling and retry logic
- Performance monitoring and alerting
- Horizontal scaling capabilities

## 🤝 Contributing

This is a proof-of-concept demonstration. For production deployment:

1. Obtain real API keys for all data sources
2. Implement proper error handling and retry logic
3. Add comprehensive logging and monitoring
4. Set up CI/CD pipelines
5. Configure production security measures

## 📝 License

This project is for demonstration purposes. Please ensure compliance with all API terms of service and data usage policies.

## 🆘 Troubleshooting

### Common Issues

**Port 8501 already in use**
```bash
docker-compose down
# Or change port in docker-compose.yml
```

**Missing API key**
- Copy .env.example to .env
- Add your Gemini API key
- Restart the application

**Build failures**
```bash
docker-compose build --no-cache
```

**Agent initialization errors**
- Check API key validity
- Verify network connectivity
- Review logs: `docker-compose logs -f`

---

*Built with ❤️ for Vietnamese financial markets using Microsoft Autogen*