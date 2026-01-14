# 🎯 Stock Debate Advisor v6 - Setup Ready ✅

**Setup Date**: January 14, 2026  
**Status**: ✅ All services prepared and ready for integration testing

---

## 📊 System Status

```
✅ PostgreSQL Database      - Running on port 5433
✅ MongoDB                  - Running on port 27017
✅ Data Service             - Configured, dependencies installed
✅ AI Service               - Configured, dependencies installed  
✅ Backend Service          - Configured, dependencies installed
✅ Frontend Service         - Configured, dependencies installed
✅ Conda Environment        - chatbot_env ready
✅ Configuration Files      - All set
✅ Local Data               - 30 financial data files available
```

---

## 🚀 Quick Start

### Start All Services in One Command
```bash
cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6
./START_SERVICES.sh
```

This will:
1. ✓ Ensure databases are running
2. ✓ Activate conda environment
3. ✓ Start Data Service (port 8001)
4. ✓ Start AI Service (port 8003)
5. ✓ Start Backend Service (port 8000)
6. ✓ Start Frontend Service (port 5174)
7. ✓ Perform health checks
8. ✓ Display service URLs and log locations

### Expected Output
```
======================================================
Stock Debate Advisor v6 - Service Startup
======================================================

1️⃣  Checking databases...
✓ Databases already running

2️⃣  Starting Data Service (port 8001)...
✓ Data Service started (PID: XXXXX)

3️⃣  Starting AI Service (port 8003)...
✓ AI Service started (PID: XXXXX)

4️⃣  Starting Backend Service (port 8000)...
✓ Backend Service started (PID: XXXXX)

5️⃣  Starting Frontend Service (port 5174)...
✓ Frontend Service started (PID: XXXXX)

Waiting for services to initialize (10 seconds)...

======================================================
Service Health Checks
======================================================

📊 Data Service:
  ✓ Running

🤖 AI Service:
  ✓ Running

🔗 Backend Service:
  ✓ Running

🌐 Frontend Service:
  ✓ Running

======================================================
✅ All services started!
======================================================

📍 Service URLs:
  Frontend: http://localhost:5174
  Backend:  http://localhost:8000
  Data:     http://localhost:8001
  AI:       http://localhost:8003
```

---

## 📋 Service Details

### Data Service (port 8001)
- **Framework**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL + MongoDB
- **Features**:
  - Financial data via Yahoo Finance API
  - News crawling from Vietnamese sources
  - REST API with v2/v3 endpoints
  - Local JSON data mode enabled (30 files)
- **Entry Point**: `uvicorn app.main:app --host 127.0.0.1 --port 8001`
- **Key Endpoints**:
  - `GET /` - Service info
  - `GET /health` - Health check
  - `GET /api/v2/company/{symbol}` - Company financial data
  - `GET /api/v3/{symbol}` - Local JSON data

### AI Service (port 8003)
- **Framework**: FastAPI + CrewAI + Google Gemini
- **Features**:
  - Multi-agent debate orchestration
  - 5 specialized agents (Fundamental, Technical, Sentiment, Moderator, Judge)
  - Session management
  - Real-time debate execution
- **Entry Point**: `python api_server.py`
- **Key Endpoints**:
  - `GET /` - Service info
  - `POST /api/debate/start` - Start debate session
  - `GET /api/sessions` - List sessions
  - `GET /api/debate/{session_id}` - Get debate result

### Backend Service (port 8000)
- **Framework**: Node.js + Express
- **Features**:
  - API gateway/bridge
  - Routes requests to Data Service and AI Service
  - Error handling and logging
  - CORS enabled for frontend
- **Entry Point**: `npm start`
- **Key Endpoints**:
  - `GET /` - Service info
  - `GET /health` - Health check with dependencies
  - `GET /api/v1/companies` - Company list
  - `GET /api/v1/financials/:symbol` - Financial data
  - `POST /api/v1/debate/start` - Start debate
  - `GET /api/v1/sessions` - Session management

### Frontend Service (port 5174)
- **Framework**: React 18 + TypeScript + Vite
- **Features**:
  - Material Design 3 components
  - Real-time debate interface
  - Stock screener
  - Financial data visualization
- **Entry Point**: `npm run dev`
- **Build**: `npm run build`

---

## 🧪 Testing Integration

After starting services, test the flow:

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. Get Company Data
```bash
curl http://localhost:8000/api/v1/companies
curl http://localhost:8000/api/v1/financials/MBB.VN
```

### 3. Start a Debate
```bash
curl -X POST http://localhost:8000/api/v1/debate/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "MBB.VN", "rounds": 3}'
```

### 4. View Frontend
Open browser: http://localhost:5174

---

## 📁 Project Structure

```
v6/
├── data-service/          # Financial data API
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── db/           # Database models
│   │   ├── api/          # API endpoints
│   │   ├── clients/      # External API clients
│   │   ├── services/     # Business logic
│   │   └── crawlers/     # News crawlers
│   └── data/
│       └── financial/    # 30 JSON files with stock data
│
├── ai-service/           # Debate orchestration
│   ├── api_server.py     # FastAPI server
│   ├── orchestrator.py   # Debate logic
│   ├── agents/           # Agent definitions
│   ├── prompts/          # System prompts
│   └── data_loader.py    # Data utilities
│
├── backend/              # API gateway
│   ├── src/
│   │   ├── index.js      # Entry point
│   │   ├── app.js        # Express setup
│   │   ├── routes/       # API routes
│   │   ├── services/     # Service clients
│   │   └── config/       # Configuration
│   └── package.json
│
├── frontend/             # React web UI
│   ├── src/
│   │   ├── App.tsx       # Main app
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── api/          # API client
│   │   └── store/        # State management
│   └── package.json
│
├── docker-compose.yml    # Database containers
├── .env                  # Root config
├── START_SERVICES.sh     # Service startup script ✓
├── VERIFY_SETUP.sh       # Verification script ✓
├── SETUP_COMPLETE.md     # Detailed docs ✓
└── README.md
```

---

## 🔧 Configuration Files

### v6/.env (Root)
```env
GEMINI_API_KEY=your_key_here
POSTGRES_URL=postgresql://postgres:postgres@localhost:5433/stock_debate_data
MONGODB_URL=mongodb://localhost:27017/
LOCAL_DATA_MODE=true
```

### backend/.env.local
```env
NODE_ENV=development
PORT=8000
DATA_SERVICE_URL=http://localhost:8001
AI_SERVICE_URL=http://localhost:8003
```

### frontend/.env.local
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENV=development
VITE_DEBATE_TIMEOUT=120000
```

---

## 📝 Environment Setup

All services use **conda environment**: `chatbot_env`

### Python Packages Installed
- FastAPI, SQLAlchemy, Pydantic (Data Service)
- CrewAI, google-generativeai (AI Service)
- pandas, yfinance, beautifulsoup4 (Data utilities)
- All other dependencies from requirements.txt

### Node Packages Installed
- Express, cors, helmet (Backend)
- React, Vite, TailwindCSS (Frontend)
- All other dependencies from package.json

---

## 🛑 Stop Services

```bash
# Stop all services
pkill -f 'uvicorn.*app.main|python.*api_server|npm run dev|npm start'

# Stop databases
cd v6
docker compose down
```

---

## 📊 Verification Results

Last run: ✅ All checks passed
```
✓ Conda environment ready
✓ Python 3.12.12 
✓ Docker 29.0.3
✓ Databases running (PostgreSQL + MongoDB)
✓ Data Service configured
✓ AI Service configured
✓ Backend Service configured
✓ Frontend Service configured
✓ 30 financial data files available
```

---

## 🎯 Next Steps

1. **Start Services**
   ```bash
   cd /home/x1e3/work/vmo/agentic/stock-debate-advisor/v6
   ./START_SERVICES.sh
   ```

2. **Wait for Services** (10 seconds for full initialization)

3. **Open Frontend**
   ```
   http://localhost:5174
   ```

4. **Test Integration**
   - Select a stock symbol
   - Start a debate session
   - Watch agents discuss the stock

5. **Monitor Logs**
   ```bash
   tail -f /tmp/data-service.log
   tail -f /tmp/ai-service.log
   tail -f /tmp/backend.log
   tail -f /tmp/frontend.log
   ```

---

## ⚠️ Troubleshooting

### Services won't start
- Check conda: `conda activate chatbot_env`
- Check databases: `docker ps | grep stock-debate`
- Check ports: `lsof -i :8000` (repeat for 8001, 8003, 5174)

### Port conflicts
- Kill process: `kill -9 <PID>`
- Or change port in service config

### Database errors
- Restart databases: `docker compose down && docker compose up -d postgres mongodb`

### API integration issues
- Check backend is running: `curl http://localhost:8000/`
- Check logs: `tail -f /tmp/backend.log`

---

**Status**: ✅ **READY FOR TESTING**

All services have been:
- ✅ Installed and configured
- ✅ Dependencies resolved
- ✅ Databases initialized
- ✅ Environment variables set
- ✅ Verified and tested

**Ready to start integration testing!**
