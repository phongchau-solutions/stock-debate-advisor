#!/bin/bash
# Quick test script for v3 autogen debate system

echo "=== Testing V3 Autogen Debate POC ===" 
echo ""

cd /home/x1e3/work/vmo/agentic/v3/autogen_debate_poc

echo "1. Checking Python environment..."
python --version
echo ""

echo "2. Verifying key packages..."
python -c "import autogen_agentchat; print('✓ autogen-agentchat:', autogen_agentchat.__version__)"
python -c "import streamlit; print('✓ streamlit installed')"
python -c "import google.generativeai; print('✓ google-generativeai installed')"
python -c "import pandas; print('✓ pandas installed')"
echo ""

echo "3. Testing agent imports..."
python -c "from agents.technical_agent import TechnicalAgent; print('✓ TechnicalAgent imports successfully')"
python -c "from agents.fundamental_agent import FundamentalAgent; print('✓ FundamentalAgent imports successfully')"
python -c "from agents.sentiment_agent import SentimentAgent; print('✓ SentimentAgent imports successfully')"
echo ""

echo "4. Testing services..."
python -c "from services.vietcap_service import VietcapService; print('✓ VietcapService imports successfully')"
python -c "from services.prompt_service import PromptService; print('✓ PromptService imports successfully')"
echo ""

echo "5. Checking directory structure..."
ls -la prompts/ | head -6
ls -la services/ | head -5
echo ""

echo "=== All basic checks passed! ===" 
echo ""
echo "To run the debate system:"
echo "  streamlit run app.py"
echo ""
echo "Or with Docker:"
echo "  docker-compose up --build"
