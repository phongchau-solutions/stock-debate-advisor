#!/bin/bash
set -euo pipefail

# Quick local setup script - runs full stack locally using docker-compose

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

ACTION="${1:-start}"

case "$ACTION" in
    start)
        log_info "Starting all services with docker-compose..."
        cd "$ROOT_DIR"
        docker-compose up -d
        
        log_info "Waiting for services to be healthy..."
        sleep 5
        
        # Check services
        docker-compose ps
        
        log_success "Services started!"
        log_info "Backend:      http://localhost:8000"
        log_info "Data Service: http://localhost:8001"
        log_info "AI Service:   http://localhost:8501"
        log_info "Frontend:     http://localhost:5173"
        ;;
    
    stop)
        log_info "Stopping all services..."
        cd "$ROOT_DIR"
        docker-compose down
        log_success "Services stopped"
        ;;
    
    restart)
        log_info "Restarting all services..."
        cd "$ROOT_DIR"
        docker-compose restart
        log_success "Services restarted"
        ;;
    
    logs)
        service="${2:-}"
        if [ -z "$service" ]; then
            log_info "Showing all logs (Ctrl+C to stop)..."
            cd "$ROOT_DIR"
            docker-compose logs -f
        else
            log_info "Showing logs for $service..."
            cd "$ROOT_DIR"
            docker-compose logs -f "$service"
        fi
        ;;
    
    status)
        cd "$ROOT_DIR"
        docker-compose ps
        ;;
    
    clean)
        log_info "Removing all containers and volumes..."
        cd "$ROOT_DIR"
        docker-compose down -v
        log_success "Cleaned"
        ;;
    
    *)
        cat << EOF
${BLUE}Stock Debate Advisor - Local Setup${NC}

Usage: $0 <action>

Actions:
    start       Start all services (default)
    stop        Stop all services
    restart     Restart all services
    logs [svc]  Show logs (optionally for specific service)
    status      Show service status
    clean       Remove containers and volumes

Services:
    postgres    PostgreSQL database
    redis       Redis cache
    backend     Node.js backend API
    data-svc    Data service API
    ai-svc      AI/Streamlit service
    frontend    React/Vite frontend

Examples:
    $0 start
    $0 logs backend
    $0 status

EOF
        ;;
esac
