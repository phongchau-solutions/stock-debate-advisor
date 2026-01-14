#!/bin/bash
# V7 Local Development Startup
# Simple: just npm run dev and streamlit run app.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Stock Debate v7 Local Development"
echo ""
echo "Starting services:"
echo "  1. Frontend (Vite): npm run dev → http://localhost:5173"
echo "  2. AI Service (Streamlit): streamlit run app.py → http://localhost:8501"
echo ""
echo "Open two terminals and run:"
echo ""
echo "Terminal 1 - Frontend:"
echo "  cd $SCRIPT_DIR/frontend"
echo "  npm install  # First time only"
echo "  npm run dev"
echo ""
echo "Terminal 2 - AI Service:"
echo "  conda activate chatbot_env"
echo "  cd $SCRIPT_DIR/ai-service"
echo "  pip install -r requirements.txt  # First time only"
echo "  streamlit run app.py"
echo ""
echo "Then visit:"
echo "  Frontend:    http://localhost:5173"
echo "  AI Service:  http://localhost:8501"
echo ""
