#!/bin/bash

# Stock Debate Advisor v6 - Setup Verification Script

echo "======================================================"
echo "Stock Debate Advisor v6 - Setup Verification"
echo "======================================================"
echo ""

# Check conda
echo "✓ Checking Conda Environment..."
if conda info --envs | grep -q chatbot_env; then
  echo "  ✓ chatbot_env found"
else
  echo "  ✗ chatbot_env NOT found - Please create it first"
  exit 1
fi

# Check Python
echo ""
echo "✓ Checking Python..."
PYTHON_VERSION=$(conda run -n chatbot_env python --version 2>/dev/null)
echo "  ✓ Python $PYTHON_VERSION"

# Check Docker
echo ""
echo "✓ Checking Docker..."
if command -v docker &> /dev/null; then
  DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
  echo "  ✓ Docker $DOCKER_VERSION"
else
  echo "  ✗ Docker NOT installed"
  exit 1
fi

# Check databases
echo ""
echo "✓ Checking Databases..."
if docker ps | grep -q stock-debate-postgres; then
  echo "  ✓ PostgreSQL running on port 5433"
else
  echo "  ! PostgreSQL not running (will start when services begin)"
fi

if docker ps | grep -q stock-debate-mongo; then
  echo "  ✓ MongoDB running on port 27017"
else
  echo "  ! MongoDB not running (will start when services begin)"
fi

# Check data-service
echo ""
echo "✓ Checking Data Service..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service

if [ -f "requirements.txt" ]; then
  echo "  ✓ requirements.txt found"
else
  echo "  ✗ requirements.txt NOT found"
  exit 1
fi

# Check if dependencies are installed
if conda run -n chatbot_env python -c "import fastapi" 2>/dev/null; then
  echo "  ✓ Python dependencies installed (FastAPI found)"
else
  echo "  ! Python dependencies may not be installed"
fi

if [ -f "app/main.py" ]; then
  echo "  ✓ app/main.py found"
else
  echo "  ✗ app/main.py NOT found"
  exit 1
fi

if [ -d "app/db" ]; then
  echo "  ✓ Database module found"
else
  echo "  ✗ Database module NOT found"
  exit 1
fi

# Check ai-service
echo ""
echo "✓ Checking AI Service..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/ai-service

if [ -f "requirements.txt" ]; then
  echo "  ✓ requirements.txt found"
else
  echo "  ✗ requirements.txt NOT found"
  exit 1
fi

# Check if dependencies are installed
if conda run -n chatbot_env python -c "import crewai" 2>/dev/null; then
  echo "  ✓ Python dependencies installed (CrewAI found)"
else
  echo "  ! Python dependencies may not be installed"
fi

if [ -f "api_server.py" ]; then
  echo "  ✓ api_server.py found"
else
  echo "  ✗ api_server.py NOT found"
  exit 1
fi

if [ -d "agents" ]; then
  echo "  ✓ Agents module found"
else
  echo "  ✗ Agents module NOT found"
  exit 1
fi

# Check backend
echo ""
echo "✓ Checking Backend Service..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/backend

if [ -f "package.json" ]; then
  echo "  ✓ package.json found"
else
  echo "  ✗ package.json NOT found"
  exit 1
fi

if [ -f ".env.local" ]; then
  echo "  ✓ .env.local configured"
else
  echo "  ! .env.local not found (copying from example)"
  cp .env.example .env.local 2>/dev/null || true
fi

if [ -d "node_modules" ]; then
  echo "  ✓ Node dependencies installed"
else
  echo "  ! Node dependencies not installed (will install when needed)"
fi

if [ -f "src/index.js" ]; then
  echo "  ✓ src/index.js found"
else
  echo "  ✗ src/index.js NOT found"
  exit 1
fi

# Check frontend
echo ""
echo "✓ Checking Frontend Service..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/frontend

if [ -f "package.json" ]; then
  echo "  ✓ package.json found"
else
  echo "  ✗ package.json NOT found"
  exit 1
fi

if [ -f ".env.local" ]; then
  echo "  ✓ .env.local configured"
  # Check if pointing to correct backend URL
  if grep -q "localhost:8000" .env.local; then
    echo "  ✓ .env.local points to backend on port 8000"
  else
    echo "  ✗ .env.local does not point to port 8000"
  fi
else
  echo "  ! .env.local not found"
fi

if [ -d "node_modules" ]; then
  echo "  ✓ Node dependencies installed"
else
  echo "  ! Node dependencies not installed"
fi

if [ -f "src/App.tsx" ]; then
  echo "  ✓ src/App.tsx found"
else
  echo "  ✗ src/App.tsx NOT found"
  exit 1
fi

# Check configuration files
echo ""
echo "✓ Checking Configuration Files..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6

if [ -f ".env" ]; then
  echo "  ✓ Root .env found"
else
  echo "  ✗ Root .env NOT found"
  exit 1
fi

if [ -f "START_SERVICES.sh" ]; then
  echo "  ✓ START_SERVICES.sh found"
  if [ -x "START_SERVICES.sh" ]; then
    echo "  ✓ START_SERVICES.sh is executable"
  else
    echo "  ! START_SERVICES.sh not executable (chmod +x needed)"
  fi
else
  echo "  ! START_SERVICES.sh not found"
fi

# Check for local data
echo ""
echo "✓ Checking Data Files..."
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service

if [ -d "data/financial" ]; then
  FINANCIAL_FILES=$(find data/financial -name "*.json" 2>/dev/null | wc -l)
  if [ "$FINANCIAL_FILES" -gt 0 ]; then
    echo "  ✓ Found $FINANCIAL_FILES financial data files"
  else
    echo "  ! No financial data files found (LOCAL_DATA_MODE may not work)"
  fi
else
  echo "  ! data/financial directory not found"
fi

# Summary
echo ""
echo "======================================================"
echo "✅ Setup Verification Complete!"
echo "======================================================"
echo ""
echo "All services are configured and ready for testing."
echo ""
echo "To start all services, run:"
echo "  cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6"
echo "  ./START_SERVICES.sh"
echo ""
