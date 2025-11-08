# Quick Start Guide

Get the Gemini Multi-Agent Stock Debate system running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git (optional)

## Step 1: Setup

```bash
# Navigate to project directory
cd /home/x1e3/work/vmo/agentic/v5/phase1/gemini-debate

# Run setup script
./setup.sh
```

## Step 2: Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

Add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

## Step 3: Run

### Option A: Local Development

```bash
# Activate conda environment
conda activate gemini-debate

# Run Streamlit app
streamlit run app.py
```

### Option B: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Step 4: Use

1. Open your browser to `http://localhost:8501`
2. Select a stock symbol from the dropdown (e.g., VCI, MBB)
3. Choose analysis timeframe
4. Click **"🚀 Start Debate"**
5. Watch the agents debate in real-time!
6. View the final verdict at the bottom

## Troubleshooting

### "No stock data found"
- Run the data converter: `python convert_data.py`
- Check that CSV files exist in `/v5/data/finance/` and `/v5/data/news/`

### "GEMINI_API_KEY is not set"
- Make sure `.env` file exists
- Verify API key is correctly set in `.env`
- Restart the application

### Import errors
- Make sure you're in the conda environment: `conda activate gemini-debate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Docker issues
- Make sure Docker is running
- Check `.env` file exists
- Verify ports 8501 is not in use

## Testing

Run the test suite to verify everything works:

```bash
python test_system.py
```

Expected output:
```
✅ PASS - Configuration
✅ PASS - Data Loader
✅ PASS - Agents
✅ PASS - Orchestrator
```

## Example Usage

Run a simple example debate:

```bash
python example_debate.py
```

This will:
1. Find available stock symbols
2. Run a complete debate for the first symbol
3. Display the full transcript
4. Export results to JSON

## What to Expect

A typical debate flow:
1. **Moderator** opens the debate (2 seconds)
2. **Round 1**: Each agent presents initial position (10-15 seconds per agent)
3. **Round 2**: Agents critique each other (10-15 seconds per agent)
4. **Round 3**: Agents respond to critiques (10-15 seconds per agent)
5. **Round 4**: Final statements (10-15 seconds per agent)
6. **Judge** renders final verdict (15-20 seconds)

Total time: ~2-3 minutes per debate

## Sample Output

```
💼 Fundamental Analyst (Round 1)
─────────────────────────────────────────────
Based on VCI's financial data, I recommend a BUY position with 
medium confidence. The company shows strong revenue growth of 15% 
YoY and maintaining healthy ROE at 12%...

📈 Technical Analyst (Round 1)
─────────────────────────────────────────────
Technical indicators suggest a HOLD position. The stock is trading 
above its 20-day MA, showing upward momentum, but RSI at 68 
indicates approaching overbought territory...

💭 Sentiment Analyst (Round 1)
─────────────────────────────────────────────
Recent news sentiment is moderately positive with an average score 
of 0.42. Notable coverage includes partnership announcements...

[... more rounds ...]

👨‍⚖️ Judge (Final Verdict)
─────────────────────────────────────────────
FINAL VERDICT: BUY - Medium Confidence

After careful consideration of all perspectives, the consensus 
points toward a BUY recommendation for VCI...
```

## Next Steps

- Customize system prompts in `prompts/` directory
- Add more data sources
- Adjust debate rounds in `.env`
- Integrate with your own data pipeline
- Deploy to cloud (AWS, GCP, Azure)

## Getting Help

- Read the full [README.md](README.md)
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture details
- Review code comments in source files
- Run tests with `python test_system.py`

## Common Commands

```bash
# Start the app
streamlit run app.py

# Run tests
python test_system.py

# Run example
python example_debate.py

# Convert data
python convert_data.py

# Check data availability
ls ../../data/finance/
ls ../../data/news/

# View logs
tail -f logs/*.log
```

Happy debating! 🎯📊
