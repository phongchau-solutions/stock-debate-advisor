#!/bin/bash

echo "🚀 Stock Debate Advisor v2 - Quick Start"
echo "========================================"

# Check environment
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found"
    exit 1
fi

# Activate environment
echo "📦 Activating chatbot_env..."
conda activate chatbot_env

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Test imports
echo "🔍 Testing imports..."
python -c "from main import app; from engine import DebateEngine; print('✅ OK')" || exit 1

# Check data store
echo "📂 Checking data_store..."
if [ -d "/home/npc11/work/stock-debate-advisor/v7/data_store/data/2026" ]; then
    echo "✅ Data store found"
    echo "   Available tickers:"
    ls /home/npc11/work/stock-debate-advisor/v7/data_store/data/2026 | head -5
else
    echo "❌ Data store not found"
    exit 1
fi

# Start API
echo ""
echo "🎯 Starting API server on http://localhost:8000..."
echo "Press Ctrl+C to stop"
echo ""
uvicorn main:app --reload --port 8000
