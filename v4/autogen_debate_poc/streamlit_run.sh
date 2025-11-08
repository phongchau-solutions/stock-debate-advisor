#!/bin/bash

# Streamlit Demo Run Script
# Usage: ./streamlit_run.sh [--api-key YOUR_API_KEY]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🚀 Multi-Agent Stock Debate PoC - Streamlit Demo${NC}"
echo "=================================================="

# Parse arguments
API_KEY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check for API key
if [ -z "$API_KEY" ]; then
    # Try to load from environment
    if [ -z "$GEMINI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  No API key provided${NC}"
        echo "Please set GEMINI_API_KEY environment variable or use --api-key"
        exit 1
    fi
    API_KEY="$GEMINI_API_KEY"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing Streamlit...${NC}"
    pip install streamlit streamlit-option-menu -q
fi

# Set environment variables
export GEMINI_API_KEY="$API_KEY"

# Run Streamlit
echo -e "${GREEN}✓${NC} Starting Streamlit demo..."
echo "📱 Access the app at: http://localhost:8501"
echo ""

streamlit run streamlit_demo.py --logger.level=info --client.showErrorDetails=true

