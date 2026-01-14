# Stock Debate Advisor v6 - Service Setup Complete ✅

All services are now prepared and ready for integration testing.

## System Architecture

```
Frontend (React)
    ↓
Backend (Node.js/Express) - Port 8000
    ├→ Data Service (FastAPI) - Port 8001
    └→ AI Service (CrewAI) - Port 8003

Databases:
    ├→ PostgreSQL - Port 5433
    └→ MongoDB - Port 27017
```

## 📋 Service Configuration Status

### 1. **PostgreSQL Database** ✅
- **Status**: Running in Docker
- **Host**: localhost:5433
- **Database**: stock_debate_data
- **User**: postgres / Password: postgres
- **Tables**: Initialized

### 2. **MongoDB** ✅
- **Status**: Running in Docker
- **Host**: localhost:27017
- **Database**: stock_debate
- **Credentials**: admin/admin

### 3. **Data Service** ✅
- **Location**: `/v6/data-service`
- **Framework**: FastAPI
- **Port**: 8001
- **Dependencies**: ✓ Installed
- **Database**: ✓ Initialized
- **Environment**: conda (chatbot_env)
- **Entry Point**: `uvicorn app.main:app --host 127.0.0.1 --port 8001`
- **Key Features**:
  - Financial data via Yahoo Finance API
  - News crawling (Vietnamese sources)
  - PostgreSQL/MongoDB integration
  - REST API with v2/v3 endpoints
  - Local data mode enabled

### 4. **AI Service** ✅
- **Location**: `/v6/ai-service`
- **Framework**: FastAPI + CrewAI
- **Port**: 8003
- **Dependencies**: ✓ Installed
- **Environment**: conda (chatbot_env)
- **Entry Point**: `python api_server.py`
- **Key Features**:
  - Multi-agent debate orchestration
  - 5 Agents:
    - Fundamental Analyst
    - Technical Analyst
    - Sentiment Analyst
    - Moderator
    - Judge
  - Session management
  - Real-time debate execution
  - Knowledge management system

### 5. **Backend Service** ✅
- **Location**: `/v6/backend`
- **Framework**: Node.js + Express
- **Port**: 8000
- **Dependencies**: ✓ Installed
- **Environment**: Node.js
- **Entry Point**: `npm start` or `node src/index.js`
- **Key Features**:
  - API gateway/bridge between frontend and services
  - Routes:
    - `/health` - Health check
    - `/api/v1/companies` - Company data
    - `/api/v1/financials` - Financial data
    - `/api/v1/debate` - Debate orchestration
    - `/api/v1/sessions` - Session management
  - Service clients for Data-Service and AI-Service
  - Error handling and logging
  - CORS enabled

### 6. **Frontend Service** ✅
- **Location**: `/v6/frontend`
- **Framework**: React 18 + TypeScript + Vite
- **Port**: 5174 (or 5173 if available)
- **Dependencies**: ✓ Installed
- **Environment**: Node.js
- **Entry Point**: `npm run dev`
- **Key Features**:
  - Material Design 3 components
  - TailwindCSS styling
  - Jotai state management
  - API integration via Axios
  - Real-time debate interface
  - Stock screener interface
  - Financial data visualization

## 🚀 How to Start Services

### Option 1: Start All Services (Recommended)
```bash
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6
./START_SERVICES.sh
```

This will:
1. Activate conda environment
2. Start PostgreSQL and MongoDB (if not running)
3. Start Data Service on port 8001
4. Start AI Service on port 8003
5. Start Backend Service on port 8000
6. Start Frontend Service on port 5174
7. Display health check results
8. Show log file locations

### Option 2: Start Services Individually

**Data Service:**
```bash
conda activate chatbot_env
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

**AI Service:**
```bash
conda activate chatbot_env
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/ai-service
python api_server.py
```

**Backend Service:**
```bash
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/backend
npm start
```

**Frontend Service:**
```bash
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/frontend
npm run dev
```

## 📍 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5174 | Web UI for stock debate |
| Backend | http://localhost:8000 | API gateway |
| Data Service | http://localhost:8001 | Financial data API |
| AI Service | http://localhost:8003 | Debate orchestration API |
| PostgreSQL | localhost:5433 | Structured data storage |
| MongoDB | localhost:27017 | Document storage |

## 🔍 Viewing Logs

All services log to `/tmp/`:
```bash
# Data Service
tail -f /tmp/data-service.log

# AI Service
tail -f /tmp/ai-service.log

# Backend Service
tail -f /tmp/backend.log

# Frontend Service
tail -f /tmp/frontend.log
```

## 🛑 Stopping Services

**Stop all services:**
```bash
pkill -f 'uvicorn.*app.main|python.*api_server|npm run dev|npm start'
```

**Stop databases:**
```bash
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6
docker compose down
```

## 🧪 Testing Integration (After Starting)

### 1. Test Health Endpoints
```bash
# Data Service
curl http://localhost:8001/

# AI Service
curl http://localhost:8003/

# Backend
curl http://localhost:8000/health
```

### 2. Test Data Endpoints
```bash
# Get companies (local data mode)
curl http://localhost:8000/api/v1/companies

# Get financial data for a stock
curl http://localhost:8000/api/v1/financials/MBB.VN
```

### 3. Test Debate Flow
```bash
# Start a debate session
curl -X POST http://localhost:8000/api/v1/debate/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "MBB.VN", "rounds": 3}'
```

## 📚 Key Files by Service

### Data Service
- `data-service/app/main.py` - FastAPI entry point
- `data-service/app/db/` - Database models and connections
- `data-service/app/api/` - API endpoints
- `data-service/data/financial/` - Local JSON data files

### AI Service
- `ai-service/api_server.py` - FastAPI server
- `ai-service/orchestrator.py` - Debate orchestration
- `ai-service/agents/` - Agent definitions
- `ai-service/prompts/` - System prompts

### Backend Service
- `backend/src/app.js` - Express app setup
- `backend/src/routes/` - API routes
- `backend/src/services/` - Service clients
- `backend/src/config/` - Configuration

### Frontend Service
- `frontend/src/pages/` - React components
- `frontend/src/api/` - API client
- `frontend/src/components/` - Reusable components
- `frontend/.env.local` - Frontend configuration

## ⚙️ Environment Variables

### Root .env (v6/.env)
```
GEMINI_API_KEY=your_key_here
POSTGRES_URL=postgresql://postgres:postgres@localhost:5433/stock_debate_data
MONGODB_URL=mongodb://localhost:27017/
LOCAL_DATA_MODE=true
```

### Backend .env.local (backend/.env.local)
```
NODE_ENV=development
PORT=8000
DATA_SERVICE_URL=http://localhost:8001
AI_SERVICE_URL=http://localhost:8003
```

### Frontend .env.local (frontend/.env.local)
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENV=development
VITE_DEBATE_TIMEOUT=120000
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8001  # or 8003, 8000, 5174

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check if containers are running
docker ps | grep stock-debate

# Restart databases
docker compose down
docker compose up -d postgres mongodb
```

### Service Not Responding
```bash
# Check logs
tail -f /tmp/[service].log

# Restart service individually
```

### Frontend Not Loading
```bash
# Check Node.js version (needs v18+)
node --version

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run dev
```

## ✅ Pre-Integration Checklist

Before starting integration tests:

- [ ] Conda environment activated: `conda activate chatbot_env`
- [ ] Docker databases running: `docker compose ps`
- [ ] All npm install commands completed
- [ ] All pip install commands completed
- [ ] Database tables initialized
- [ ] All .env files configured
- [ ] START_SERVICES.sh script executable
- [ ] No services currently running

## 🎯 Next Steps

1. Run `./START_SERVICES.sh` to start all services
2. Check health endpoints to verify all services are running
3. Open frontend at http://localhost:5174
4. Test debate flow through the UI
5. Monitor logs for any issues

---

**Setup completed on**: January 14, 2026
**Version**: v6 Microservices
