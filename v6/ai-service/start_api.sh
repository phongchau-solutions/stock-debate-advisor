#!/bin/bash
# FastAPI server startup script for Stock Debate Advisor

set -e

CONDA_ENV="chatbot_env"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "🚀 Stock Debate Advisor - FastAPI + Frontend Setup"
echo ""

# Check if conda environment exists
if ! conda env list | grep -q "^${CONDA_ENV} "; then
    echo "⚠️  Conda environment '${CONDA_ENV}' not found."
    echo "📝 Please run ./setup.sh first"
    exit 1
fi

# Activate conda environment
echo "🔄 Activating conda environment: $CONDA_ENV..."
source activate $CONDA_ENV

# Verify API key
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "📝 Please run ./setup.sh first or create .env with GEMINI_API_KEY"
    exit 1
fi

if ! grep -q "GEMINI_API_KEY" .env; then
    echo "⚠️  GEMINI_API_KEY not found in .env"
    exit 1
fi

# Check if requirements are installed
echo "📚 Checking dependencies..."
python -c "import fastapi; import uvicorn" || {
    echo "📥 Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
}

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Available services:"
echo ""
echo "1️⃣  FastAPI Backend:"
echo "   URL: http://$API_HOST:$API_PORT"
echo "   Docs: http://$API_HOST:$API_PORT/docs"
echo "   ReDoc: http://$API_HOST:$API_PORT/redoc"
echo ""
echo "2️⃣  Frontend (React/Node.js):"
echo "   URL: http://localhost:$FRONTEND_PORT"
echo "   Location: ../frontend/"
echo ""
echo "🎯 To start the services:"
echo ""
echo "Terminal 1 - Start FastAPI server:"
echo "  python -m uvicorn api_server:app --host $API_HOST --port $API_PORT --reload"
echo ""
echo "Terminal 2 - Start Frontend (from ../frontend/):"
echo "  npm run dev"
echo ""
echo "📖 API Endpoints:"
echo "  GET  /api/symbols              - List available stocks"
echo "  POST /api/debate/start         - Start a debate"
echo "  GET  /api/debate/status/{id}   - Check debate progress"
echo "  GET  /api/debate/result/{id}   - Get debate results"
echo "  GET  /api/sessions             - List all sessions"
echo ""
