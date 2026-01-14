#!/bin/bash
# Local development setup and testing
# Usage: ./scripts/local-dev.sh [start|stop|test|rebuild]

ACTION=${1:-start}
PROJECT_ROOT=$(pwd)

echo "🛠️  Stock Debate Advisor - Local Development"
echo "   Action: $ACTION"

case $ACTION in
    start)
        echo ""
        echo "🚀 Starting local development environment..."
        
        # Check for .env
        if [ ! -f .env ]; then
            echo "⚠️  .env file not found. Creating from .env.example..."
            cp .env.example .env
            echo "   Please update .env with your API keys"
        fi
        
        # Start Docker Compose
        echo "📦 Starting Docker services..."
        docker-compose up -d
        
        echo ""
        echo "✅ Services started!"
        echo "   AI Service API: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo "   Data Service: http://localhost:8001"
        echo ""
        echo "📊 Docker status:"
        docker-compose ps
        ;;
    
    stop)
        echo ""
        echo "🛑 Stopping local development environment..."
        docker-compose down
        echo "✅ Services stopped"
        ;;
    
    test)
        echo ""
        echo "🧪 Running tests..."
        
        # Test API health
        echo "   Testing API health..."
        curl -s http://localhost:8000/health | python -m json.tool
        
        echo ""
        echo "   Testing /docs endpoint..."
        curl -s http://localhost:8000/docs | head -20
        
        echo ""
        echo "   Running pytest..."
        python -m pytest tests/ -v --tb=short
        ;;
    
    rebuild)
        echo ""
        echo "🔨 Rebuilding Docker images..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        
        echo ""
        echo "✅ Services rebuilt and started!"
        docker-compose ps
        ;;
    
    logs)
        echo ""
        echo "📋 AI Service logs:"
        docker-compose logs -f ai-service
        ;;
    
    *)
        echo "Usage: $0 [start|stop|test|rebuild|logs]"
        exit 1
        ;;
esac
