# Quick Start Guide - Stock Debate Advisor V5

Get the multi-agent debate system running in 5 minutes.

## Prerequisites

Choose one:
- **Option A**: Docker & Docker Compose (Recommended)
- **Option B**: Python 3.11+ & pip

## Option A: Docker (Easiest - 3 Commands)

### 1. Get Your API Key

Visit [Google AI Studio](https://ai.google.dev/) and get a free Gemini API key.

### 2. Configure Environment

```bash
cd v5
cp .env.example .env
```

Edit `.env` and add your key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Launch

```bash
docker compose up --build
```

Wait for:
```
stock-debate-v5  | You can now view your Streamlit app in your browser.
stock-debate-v5  | URL: http://localhost:8501
```

### 4. Open Browser

Navigate to: **http://localhost:8501**

Done! 🎉

---

## Option B: Local Python Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd stock-debate-advisor/v5
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```bash
GEMINI_API_KEY=your_actual_api_key_here
FINANCE_DATA_PATH=./data/finance
NEWS_DATA_PATH=./data/news
```

### 5. Run

```bash
streamlit run app.py
```

Browser opens automatically at: **http://localhost:8501**

---

## Using the Application

### 1. Select Stock

In the sidebar, choose a stock symbol from the dropdown (e.g., VNM, VCB, HPG).

### 2. Start Debate

Click **"Start Debate"** button.

### 3. Watch Real-time Analysis

You'll see:
- **Round 1**: Each agent presents initial analysis
- **Round 2+**: Agents critique each other
- **Judge Commentary**: Quality assessment after each round
- **Final Verdict**: BUY/HOLD/SELL recommendation

### 4. Review Results

- Scroll through the debate transcript
- Check each agent's reasoning
- Review the final verdict and rationale

---

## Data Setup

### Sample Data Structure

The system expects CSV files in:

```
v5/
└── data/
    ├── finance/
    │   ├── VNM_financials.csv
    │   ├── VNM_ohlc.csv
    │   ├── VCB_financials.csv
    │   └── VCB_ohlc.csv
    └── news/
        ├── VNM_news.csv
        └── VCB_news.csv
```

### Financial Data Format

**{SYMBOL}_financials.csv**:
```csv
metric,value,period
revenue,25000000000,2024-Q3
net_income,3500000000,2024-Q3
total_assets,45000000000,2024-Q3
pe_ratio,15.5,2024-Q3
roe,18.2,2024-Q3
debt_to_equity,0.45,2024-Q3
```

**{SYMBOL}_ohlc.csv**:
```csv
date,open,high,low,close,volume
2024-10-01,85000,87000,84000,86500,1250000
2024-10-02,86500,88000,85500,87200,1180000
```

### News Data Format

**{SYMBOL}_news.csv**:
```csv
date,title,content,source
2024-10-15,"VNM tăng trưởng mạnh Q3","Vinamilk công bố kết quả kinh doanh...",VnExpress
2024-10-10,"Thị trường sữa cạnh tranh","Ngành sữa Việt Nam đối mặt...",CafeF
```

---

## Troubleshooting

### Issue: "No stocks available"

**Cause**: No data files in `data/finance/` or `data/news/`

**Solution**:
```bash
# Check if data directory exists
ls -la data/finance/
ls -la data/news/

# Add sample CSV files following the format above
```

### Issue: "GEMINI_API_KEY not set"

**Cause**: Missing or incorrect `.env` configuration

**Solution**:
```bash
# Check .env file exists
cat .env

# Verify key is set
grep GEMINI_API_KEY .env

# Should output:
# GEMINI_API_KEY=your_key_here
```

### Issue: "Connection refused" or "Port 8501 in use"

**Cause**: Port conflict

**Solution for Docker**:
```bash
# Stop existing container
docker compose down

# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead

# Restart
docker compose up
```

**Solution for Local**:
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Issue: Agents produce generic responses

**Cause**: Data files empty or incorrectly formatted

**Solution**:
```bash
# Verify data files have content
head data/finance/VNM_financials.csv
head data/news/VNM_news.csv

# Check CSV format matches examples above
```

---

## Configuration Options

Edit `.env` to customize:

```bash
# LLM Settings
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash      # or gemini-1.5-pro
TEMPERATURE=0.7                     # 0.0 = deterministic, 1.0 = creative

# Data Paths
FINANCE_DATA_PATH=./data/finance
NEWS_DATA_PATH=./data/news

# Debate Settings
MIN_ROUNDS=2                        # Minimum debate rounds
MAX_ROUNDS=10                       # Maximum debate rounds
```

---

## Next Steps

### 1. Add Your Own Data

Place your Vietnamese stock data in `data/finance/` and `data/news/` following the formats above.

### 2. Customize Agent Prompts

Edit system prompts in `prompts/`:
- `fundamental_agent.txt` - Adjust financial analysis focus
- `technical_agent.txt` - Modify technical indicators
- `sentiment_agent.txt` - Change sentiment analysis approach
- `moderator_agent.txt` - Alter debate flow
- `judge_agent.txt` - Adjust evaluation criteria

### 3. Experiment with Models

Try different Gemini models in `.env`:
```bash
# Faster, cheaper
GEMINI_MODEL=gemini-1.5-flash

# More capable, slower
GEMINI_MODEL=gemini-1.5-pro
```

### 4. Adjust Temperature

Lower temperature = more consistent, focused analysis:
```bash
TEMPERATURE=0.3
```

Higher temperature = more creative, diverse perspectives:
```bash
TEMPERATURE=0.9
```

---

## Useful Commands

### Docker

```bash
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build

# Remove all data
docker compose down -v
```

### Local

```bash
# Activate environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Run with custom config
streamlit run app.py --server.port 8502

# Deactivate environment
deactivate
```

---

## Support

**Documentation**:
- [README.md](README.md) - Full documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details

**Need Help?**:
- Check data file formats match examples
- Verify API key is valid
- Ensure Python 3.11+ or Docker is installed
- Review logs for error messages

---

**Ready to Analyze Stocks!** 🚀📈

Start with well-known Vietnamese stocks like VNM, VCB, or HPG to see the system in action.
