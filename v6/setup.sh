#!/bin/bash

# Setup script for v6 Stock Debate System
set -e

echo "🚀 Setting up Stock Debate v6 Microservices System..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo "✅ Docker Compose found"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi
echo "✅ Python found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 0
fi

# Check if API key is set
if grep -q "your_gemini_api_key_here" .env; then
    echo "❌ Please set your GEMINI_API_KEY in .env file"
    exit 1
fi
echo "✅ Environment configured"

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/postgres
mkdir -p data/mongodb
mkdir -p data/airflow/logs
echo "✅ Data directories created"

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build --no-cache

# Start databases first
echo -e "${YELLOW}Starting databases...${NC}"
docker-compose up -d postgres mongodb

# Wait for databases to be healthy
echo "Waiting for databases to be ready..."
sleep 10

# Initialize databases
echo -e "${YELLOW}Initializing databases...${NC}"
docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE IF NOT EXISTS stock_debate_data;"
echo "✅ Databases initialized"

# Start all services
echo -e "${YELLOW}Starting all services...${NC}"
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 15

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

check_service() {
    local service_name=$1
    local url=$2
    
    if curl -s -o /dev/null -w "%{http_code}" $url | grep -q "200\|404"; then
        echo "✅ $service_name is running"
    else
        echo "⚠️  $service_name may not be ready yet"
    fi
}

check_service "Data Service" "http://localhost:8001/health"
check_service "Analysis Service" "http://localhost:8002/health"
check_service "Agentic Service (Streamlit)" "http://localhost:8501"

# Display access information
echo -e "${GREEN}"
echo "============================================"
echo "✅ Stock Debate v6 System is ready!"
echo "============================================"
echo ""
echo "Access Points:"
echo "  📊 Agentic Service Demo: http://localhost:8501"
echo "  📡 Data Service API:     http://localhost:8001/docs"
echo "  🔬 Analysis Service API: http://localhost:8002/docs"
echo "  📅 Airflow UI:           http://localhost:8080 (admin/admin)"
echo ""
echo "Quick Test:"
echo "  curl http://localhost:8001/health"
echo "  curl http://localhost:8002/health"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "============================================"
echo -e "${NC}"

# Optional: Run a test debate
read -p "Would you like to run a test debate? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running test debate for MBB...${NC}"
    curl -X POST http://localhost:8002/api/v1/analyze/MBB
    echo ""
    echo "✅ Test complete! Check the output above."
    echo "   Open http://localhost:8501 to run interactive debates"
fi

echo -e "${GREEN}Setup complete! Happy debugging! 🎉${NC}"
