#!/bin/bash

# Stock Debate Advisor v6 - Service Startup Script
# This script starts all services for integration testing

set -e

echo "======================================================"
echo "Stock Debate Advisor v6 - Service Startup"
echo "======================================================"

# Activate conda environment
source /home/x1e3/miniconda3/etc/profile.d/conda.sh
conda activate chatbot_env

PROJECT_DIR="/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6"
cd "$PROJECT_DIR"

# Ensure databases are running
echo ""
echo "1️⃣  Checking databases..."
if ! docker ps | grep -q stock-debate-postgres; then
  echo "Starting PostgreSQL and MongoDB..."
  docker compose up -d postgres mongodb
  sleep 10
  echo "✓ Databases started"
else
  echo "✓ Databases already running"
fi

# Start Data Service
echo ""
echo "2️⃣  Starting Data Service (port 8001)..."
cd "$PROJECT_DIR/data-service"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/data-service.log 2>&1 &
DATA_SERVICE_PID=$!
echo "✓ Data Service started (PID: $DATA_SERVICE_PID)"

# Start AI Service
echo ""
echo "3️⃣  Starting AI Service (port 8003)..."
cd "$PROJECT_DIR/ai-service"
nohup python api_server.py > /tmp/ai-service.log 2>&1 &
AI_SERVICE_PID=$!
echo "✓ AI Service started (PID: $AI_SERVICE_PID)"

# Start Backend Service
echo ""
echo "4️⃣  Starting Backend Service (port 8000)..."
cd "$PROJECT_DIR/backend"
nohup npm start > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend Service started (PID: $BACKEND_PID)"

# Start Frontend Service
echo ""
echo "5️⃣  Starting Frontend Service (port 5174)..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✓ Frontend Service started (PID: $FRONTEND_PID)"

# Wait for services to start
echo ""
echo "Waiting for services to initialize (10 seconds)..."
sleep 10

# Health checks
echo ""
echo "======================================================"
echo "Service Health Checks"
echo "======================================================"

echo ""
echo "📊 Data Service:"
curl -s http://localhost:8001/ | python -m json.tool 2>/dev/null | head -5 && echo "  ✓ Running" || echo "  ✗ Not responding"

echo ""
echo "🤖 AI Service:"
curl -s http://localhost:8003/ | python -m json.tool 2>/dev/null | head -5 && echo "  ✓ Running" || echo "  ✗ Not responding"

echo ""
echo "🔗 Backend Service:"
curl -s http://localhost:8000/ | python -m json.tool 2>/dev/null | head -5 && echo "  ✓ Running" || echo "  ✗ Not responding"

echo ""
echo "🌐 Frontend Service:"
curl -s http://localhost:5174/ | grep -q "Stock Debate Advisor" && echo "  ✓ Running" || echo "  ✗ Not responding"

echo ""
echo "======================================================"
echo "✅ All services started!"
echo "======================================================"
echo ""
echo "📍 Service URLs:"
echo "  Frontend: http://localhost:5174"
echo "  Backend:  http://localhost:8000"
echo "  Data:     http://localhost:8001"
echo "  AI:       http://localhost:8003"
echo ""
echo "📋 Logs:"
echo "  Data Service:     tail -f /tmp/data-service.log"
echo "  AI Service:       tail -f /tmp/ai-service.log"
echo "  Backend Service:  tail -f /tmp/backend.log"
echo "  Frontend Service: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "  pkill -f 'uvicorn.*app.main\|python.*api_server\|npm run dev\|npm start'"
echo ""
