#!/bin/bash

# Autogen Financial Debate POC - Run Script
# This script provides easy commands to manage the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your API keys before running the application."
        echo "Required: GEMINI_API_KEY"
        echo "Optional: VIETCAP_API_KEY"
        return 1
    fi
    return 0
}

# Function to display help
show_help() {
    echo "Autogen Financial Debate POC - Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Initial setup (copy .env template)"
    echo "  build     - Build Docker images"
    echo "  start     - Start the application"
    echo "  stop      - Stop the application"
    echo "  restart   - Restart the application"
    echo "  logs      - Show application logs"
    echo "  clean     - Clean up containers and images"
    echo "  status    - Show application status"
    echo "  test      - Run test with VNM stock"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # First time setup"
    echo "  $0 start     # Start the application"
    echo "  $0 logs      # View logs"
    echo ""
}

# Setup function
setup() {
    print_status "Setting up Autogen Financial Debate POC..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file and add your API keys:"
        print_warning "  - GEMINI_API_KEY (Required)"
        print_warning "  - VIETCAP_API_KEY (Optional)"
        echo ""
        echo "You can edit the file using:"
        echo "  nano .env"
        echo "  vim .env"
        echo "  code .env"
    else
        print_warning ".env file already exists"
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    print_success "Logs directory created"
    
    print_success "Setup completed!"
    print_status "Next steps:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Run: $0 start"
}

# Build function
build() {
    print_status "Building Docker images..."
    check_docker
    
    docker-compose build
    print_success "Docker images built successfully"
}

# Start function
start() {
    print_status "Starting Autogen Financial Debate POC..."
    check_docker
    
    if ! check_env; then
        print_error "Please setup environment first: $0 setup"
        exit 1
    fi
    
    # Check if GEMINI_API_KEY is set
    source .env
    if [ -z "$GEMINI_API_KEY" ]; then
        print_error "GEMINI_API_KEY is not set in .env file"
        exit 1
    fi
    
    docker-compose up -d --build
    
    print_success "Application started successfully!"
    print_status "Access the application at: http://localhost:8501"
    print_status "View logs with: $0 logs"
}

# Stop function
stop() {
    print_status "Stopping application..."
    check_docker
    
    docker-compose down
    print_success "Application stopped"
}

# Restart function
restart() {
    print_status "Restarting application..."
    stop
    sleep 2
    start
}

# Logs function
show_logs() {
    print_status "Showing application logs..."
    check_docker
    
    docker-compose logs -f
}

# Clean function
clean() {
    print_warning "This will remove all containers, images, and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        check_docker
        
        docker-compose down -v --rmi all --remove-orphans
        docker system prune -f
        
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Status function
show_status() {
    print_status "Application status:"
    check_docker
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Application is running"
        docker-compose ps
        echo ""
        print_status "Application URL: http://localhost:8501"
        print_status "Health check: http://localhost:8501/_stcore/health"
    else
        print_warning "Application is not running"
        print_status "Start with: $0 start"
    fi
}

# Test function
test_application() {
    print_status "Testing application with VNM stock..."
    
    # Check if application is running
    if ! curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        print_error "Application is not running or not healthy"
        print_status "Start the application first: $0 start"
        exit 1
    fi
    
    print_success "Application is running and healthy"
    print_status "Test steps:"
    echo "  1. Open http://localhost:8501 in your browser"
    echo "  2. Enter your Gemini API key in the sidebar"
    echo "  3. Use stock symbol: VNM"
    echo "  4. Select period: 30 days"
    echo "  5. Click 'Start Debate'"
    echo "  6. Observe the multi-agent debate process"
    echo "  7. Review the final BUY/HOLD/SELL recommendation"
    echo ""
    print_status "Expected result: Interactive debate leading to investment decision"
}

# Main script logic
case "${1:-help}" in
    setup)
        setup
        ;;
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean
        ;;
    status)
        show_status
        ;;
    test)
        test_application
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac