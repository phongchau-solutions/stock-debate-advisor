#!/bin/bash

################################################################################
# Stock Debate Advisor v6 - Main Entry Point
# 
# This is the primary entry point for starting all services for the Stock
# Debate Advisor system. It handles:
# - Environment setup and validation
# - Service startup orchestration
# - Health checks and verification
# - Logging and error handling
#
# Usage: ./main.sh [start|stop|restart|logs|status|clean|help]
################################################################################

set -euo pipefail

# ============================================================================
# Configuration & Constants
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
SERVICES_LOG_DIR="${PROJECT_ROOT}/.logs"
PID_FILE="${PROJECT_ROOT}/.pids"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Service ports
declare -A SERVICE_PORTS=(
    ["backend"]=8000
    ["data-service"]=8001
    ["ai-service"]=8501
    ["frontend"]=5173
    ["localstack"]=4566
)

# Service URLs
declare -A SERVICE_URLS=(
    ["backend"]="http://localhost:8000/health"
    ["data-service"]="http://localhost:8001/docs"
    ["ai-service"]="http://localhost:8501"
    ["frontend"]="http://localhost:5173"
)

# ============================================================================
# Logging Functions
# ============================================================================

log_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

log_section() {
    echo -e "\n${CYAN}➜ $*${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*"
}

# ============================================================================
# Utility Functions
# ============================================================================

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

ensure_directory() {
    mkdir -p "$1" || {
        log_error "Failed to create directory: $1"
        return 1
    }
}

wait_for_port() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if nc -z localhost "$port" 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    return 1
}

wait_for_url() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    return 1
}

# ============================================================================
# Validation & Pre-checks
# ============================================================================

validate_environment() {
    log_section "Validating environment"
    
    local failed=0
    
    # Check required commands
    for cmd in docker docker-compose curl nc; do
        if check_command "$cmd"; then
            log_success "$cmd available"
        else
            log_error "$cmd not found"
            failed=1
        fi
    done
    
    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env file not found, creating from .env.example"
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_success ".env created from template"
        else
            log_error ".env.example not found"
            failed=1
        fi
    else
        log_success ".env file exists"
    fi
    
    # Check Docker daemon
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        failed=1
    else
        log_success "Docker daemon is running"
    fi
    
    # Check Docker Compose version
    local compose_version=$(docker-compose --version | awk '{print $3}')
    log_success "Docker Compose version: $compose_version"
    
    if [ $failed -eq 1 ]; then
        log_error "Environment validation failed!"
        return 1
    fi
    
    log_success "Environment validation passed"
    return 0
}

# ============================================================================
# Service Management Functions
# ============================================================================

start_services() {
    log_header "Starting Stock Debate Advisor v6 Services"
    
    # Validate environment first
    if ! validate_environment; then
        log_error "Environment validation failed. Cannot proceed."
        return 1
    fi
    
    # Create necessary directories
    ensure_directory "$SERVICES_LOG_DIR"
    ensure_directory "$PID_FILE"
    
    log_section "Starting Docker containers with docker-compose"
    cd "$PROJECT_ROOT"
    
    # Start all services
    if docker-compose up -d; then
        log_success "Docker containers started"
    else
        log_error "Failed to start Docker containers"
        return 1
    fi
    
    # Wait for databases
    log_section "Waiting for LocalStack to be healthy"
    
    if wait_for_port 4566; then
        log_success "LocalStack is healthy (port 4566)"
    else
        log_error "LocalStack failed to become healthy"
        return 1
    fi
    
    # Wait for services
    log_section "Waiting for services to start"
    
    for service in "data-service" "ai-service" "backend"; do
        local port=${SERVICE_PORTS[$service]}
        log_info "Waiting for $service (port $port)..."
        
        if wait_for_port "$port"; then
            log_success "$service is ready (port $port)"
        else
            log_warning "$service may not be responding (port $port)"
        fi
    done
    
    # Display service information
    log_section "Service Status"
    docker-compose ps
    
    log_header "✓ All Services Started Successfully"
    
    return 0
}

stop_services() {
    log_section "Stopping all services"
    cd "$PROJECT_ROOT"
    
    if docker-compose down; then
        log_success "All services stopped"
        return 0
    else
        log_error "Failed to stop services"
        return 1
    fi
}

restart_services() {
    log_section "Restarting all services"
    
    if stop_services && sleep 2 && start_services; then
        log_success "Services restarted"
        return 0
    else
        log_error "Failed to restart services"
        return 1
    fi
}

show_logs() {
    local service="${1:-}"
    cd "$PROJECT_ROOT"
    
    if [ -z "$service" ]; then
        log_info "Showing all service logs (Ctrl+C to exit)..."
        docker-compose logs -f
    else
        log_info "Showing logs for $service (Ctrl+C to exit)..."
        docker-compose logs -f "$service"
    fi
}

show_status() {
    log_section "Service Status"
    cd "$PROJECT_ROOT"
    docker-compose ps
}

clean_services() {
    log_warning "Removing all containers, networks, and volumes..."
    cd "$PROJECT_ROOT"
    
    read -p "Are you sure? This will delete all data. (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        if docker-compose down -v; then
            log_success "All containers and volumes removed"
            rm -rf "$SERVICES_LOG_DIR" "$PID_FILE" 2>/dev/null || true
            log_success "Cleaned"
            return 0
        else
            log_error "Failed to clean"
            return 1
        fi
    else
        log_info "Clean cancelled"
        return 0
    fi
}

verify_services() {
    log_section "Verifying Services"
    
    local failed=0
    
    for service in "data-service" "ai-service" "backend"; do
        local url=${SERVICE_URLS[$service]}
        log_info "Checking $service at $url..."
        
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "$service is responding"
        else
            log_warning "$service may not be fully ready yet"
        fi
    done
    
    log_section "Access Points"
    echo ""
    echo "Backend API:      ${BLUE}http://localhost:${SERVICE_PORTS[backend]}${NC}"
    echo "Data Service API: ${BLUE}http://localhost:${SERVICE_PORTS[data-service]}/docs${NC}"
    echo "AI Service Demo:  ${BLUE}http://localhost:${SERVICE_PORTS[ai-service]}${NC}"
    echo "Frontend UI:      ${BLUE}http://localhost:${SERVICE_PORTS[frontend]}${NC}"
    echo "LocalStack:       ${BLUE}http://localhost:${SERVICE_PORTS[localstack]}${NC} (DynamoDB, S3, SQS)"
    echo ""
    
    return 0
}

# ============================================================================
# Help & Usage
# ============================================================================

show_help() {
    cat << EOF
${BLUE}Stock Debate Advisor v6 - Main Entry Point${NC}

${CYAN}Usage:${NC}
    ./main.sh [COMMAND] [OPTIONS]

${CYAN}Commands:${NC}
    start       Start all services (default if no command specified)
    stop        Stop all services gracefully
    restart     Restart all services
    logs        Show service logs in real-time
    status      Display current service status
    verify      Verify that all services are accessible
    clean       Remove all containers and volumes (WARNING: deletes data)
    help        Show this help message

${CYAN}Service Ports:${NC}
    Backend:        ${SERVICE_PORTS[backend]}
    Data Service:   ${SERVICE_PORTS[data-service]}
    AI Service:     ${SERVICE_PORTS[ai-service]}
    Frontend:       ${SERVICE_PORTS[frontend]}
    LocalStack:     ${SERVICE_PORTS[localstack]}

${CYAN}Examples:${NC}
    ./main.sh                    # Start all services
    ./main.sh start              # Same as above
    ./main.sh stop               # Stop all services
    ./main.sh restart            # Restart all services
    ./main.sh logs               # Show all logs
    ./main.sh logs data-service  # Show data service logs
    ./main.sh status             # Show service status
    ./main.sh verify             # Verify all services are accessible

${CYAN}Documentation:${NC}
    - README.md for architecture overview
    - QUICKSTART.md for quick setup
    - docker-compose.yml for service definitions

EOF
}

# ============================================================================
# Main Entry Point
# ============================================================================

main() {
    local command="${1:-start}"
    
    case "$command" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        status)
            show_status
            ;;
        verify)
            verify_services
            ;;
        clean)
            clean_services
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
