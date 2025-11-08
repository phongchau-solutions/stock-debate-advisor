# Autogen Financial Debate POC - Deployment Guide


QUICK START GUIDE:

1. Prerequisites:
   - Docker and Docker Compose installed
   - Google Gemini API key

2. Setup:
   cd autogen_debate_poc
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY

3. Run:
   ./run.sh start
   # Or: docker-compose up --build

4. Access:
   Open http://localhost:8501

5. Test:
   - Enter your Gemini API key in sidebar
   - Use stock symbol: VNM
   - Select period: 30 days
   - Click "Start Debate"
   - Observe multi-agent discussion
   - Review final BUY/HOLD/SELL recommendation

SUCCESS CRITERIA:
✅ Functional Autogen multi-agent debate (≥3 rounds)
✅ Real-time Streamlit visualization
✅ Structured final recommendation with rationale
✅ Dockerized environment runs with: docker-compose up
✅ Code ready for Gemini API key injection
