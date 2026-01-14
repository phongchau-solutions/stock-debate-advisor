# AI Service Directory Structure

```
ai-service/
├── src/                          # Source code
│   ├── __init__.py
│   ├── core/                     # Core engine and configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and environment config
│   │   ├── constants.py         # Constants and agent prompts
│   │   ├── engine.py            # Gemini-powered debate engine
│   │   └── engine_bedrock.py    # AWS Bedrock-powered debate engine
│   ├── handlers/                 # Lambda and API handlers
│   │   ├── __init__.py
│   │   ├── index.py             # AWS Lambda entry point
│   │   ├── main.py              # FastAPI application server
│   │   ├── demo.py              # Streamlit demo application
│   │   └── migrate_data.py      # Data migration Lambda
│   └── utils/                    # Utilities and models
│       ├── __init__.py
│       └── models.py            # Pydantic models for API
├── deps/                         # Dependencies by environment
│   ├── requirements-prod.txt    # Production (Lambda, API)
│   ├── requirements-dev.txt     # Development (pytest, linting)
│   ├── requirements-demo.txt    # Demo (streamlit, plotly)
│   └── requirements-health.txt  # Health check (stdlib only)
├── scripts/                      # Shell scripts (symlinks to /scripts)
└── README.md                     # Documentation

# Old files removed
- requirements*.txt (consolidated to deps/)
- QUICK_START.sh (moved to /scripts/ai-service-quickstart.sh)

# Shell scripts location
All scripts are in: /scripts/
- ai-service-quickstart.sh       # Quick start guide
- dev-local.sh                   # Local development setup
- deploy.sh                      # Deployment script
- health-check.sh                # Health monitoring
- etc.
```

## Installation

By environment:

```bash
# Production
pip install -r ai-service/deps/requirements-prod.txt

# Development
pip install -r ai-service/deps/requirements-dev.txt

# Demo/Streamlit
pip install -r ai-service/deps/requirements-demo.txt

# Health check Lambda
# No dependencies needed
```

## Running

```bash
# API server
python -m src.handlers.main

# Demo
streamlit run ai-service/src/handlers/demo.py

# Quick start
./scripts/ai-service-quickstart.sh
```
