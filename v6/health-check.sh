#!/bin/bash

################################################################################
# Stock Debate Advisor v6 - Health Check & Service Verification
#
# This script verifies that all services are running and accessible.
# It performs comprehensive health checks on all components.
################################################################################

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Health check configuration
TIMEOUT=5
MAX_RETRIES=3
RETRY_DELAY=2

# ============================================================================
# Service Configuration
# ============================================================================

declare -A SERVICES=(
    ["LocalStack"]=":4566"
    ["Backend API"]=":8000"
    ["Data Service"]=":8001"
    ["AI Service"]=":8501"
    ["Frontend"]=":5173"
)

declare -A ENDPOINTS=(
    ["Backend API"]="http://localhost:8000/health"
    ["Data Service API"]="http://localhost:8001/docs"
    ["AI Service"]="http://localhost:8501"
    ["Frontend"]="http://localhost:5173"
)

# ============================================================================
# Output Functions
# ============================================================================

log_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

log_section() {
    echo -e "\n${CYAN}➜ $*${NC}"
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

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

# ============================================================================
# Check Functions
# ============================================================================

check_port() {
    local service=$1
    local port=${2##:}  # Remove leading colon
    
    if nc -z localhost "$port" 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
        return 0
    fi
    return 1
}

check_http_endpoint() {
    local service=$1
    local url=$2
    
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 500 ]; then
        return 0
    fi
    return 1
}

check_docker_container() {
    local container=$1
    
    if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^${container}$"; then
        return 0
    fi
    return 1
}

# ============================================================================
# Main Health Checks
# ============================================================================

check_docker_daemon() {
    log_section "Checking Docker Daemon"
    
    if docker info > /dev/null 2>&1; then
        local version=$(docker --version)
        log_success "Docker is running: $version"
        return 0
    else
        log_error "Docker daemon is not running"
        return 1
    fi
}

check_docker_compose() {
    log_section "Checking Docker Compose"
    
    if command -v docker-compose &> /dev/null; then
        local version=$(docker-compose --version)
        log_success "Docker Compose available: $version"
        return 0
    else
        log_error "Docker Compose not found"
        return 1
    fi
}

check_containers() {
    log_section "Checking Docker Containers"
    
    cd "$PROJECT_ROOT"
    
    local containers=$(docker-compose ps --services 2>/dev/null)
    local running=$(docker-compose ps -q 2>/dev/null | wc -l)
    local total=$(docker-compose config --services 2>/dev/null | wc -l)
    
    if [ -z "$running" ]; then
        running=0
    fi
    
    log_info "Running containers: $running / $total"
    
    echo ""
    docker-compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    if [ "$running" -eq "$total" ] && [ "$total" -gt 0 ]; then
        log_success "All containers are running"
        return 0
    else
        if [ "$total" -eq 0 ]; then
            log_warning "No containers configured"
            return 1
        else
            log_warning "Not all containers are running ($running/$total)"
            return 1
        fi
    fi
}

check_database_services() {
    log_section "Checking LocalStack (DynamoDB)"
    
    local localstack_ok=0
    
    # Check LocalStack
    log_info "Checking LocalStack on port 4566..."
    if check_port "LocalStack" ":4566"; then
        log_success "LocalStack is accessible"
        localstack_ok=1
    else
        log_error "LocalStack is not accessible"
    fi
    
    [ "$localstack_ok" -eq 1 ] && return 0 || return 1
}

check_api_services() {
    log_section "Checking API Services Health"
    
    local all_ok=1
    
    for service in "Backend API" "Data Service API" "AI Service"; do
        local url=${ENDPOINTS[$service]}
        local port=${url##*:}
        port=${port%%/*}
        
        log_info "Checking $service at $url..."
        
        # First check if port is open
        if check_port "$service" ":$port"; then
            # Then check HTTP endpoint if available
            if [[ $service == *"API"* ]]; then
                if check_http_endpoint "$service" "$url"; then
                    log_success "$service is responding"
                else
                    log_warning "$service port is open but not responding to HTTP"
                fi
            else
                log_success "$service is responding"
            fi
        else
            log_error "$service is not accessible (port $port)"
            all_ok=0
        fi
    done
    
    return $((1 - all_ok))
}

check_frontend() {
    log_section "Checking Frontend"
    
    local url=${ENDPOINTS["Frontend"]}
    log_info "Checking Frontend at $url..."
    
    if check_port "Frontend" ":5173"; then
        log_success "Frontend port is open (5173)"
        return 0
    else
        log_error "Frontend is not accessible (port 5173)"
        return 1
    fi
}

check_environment() {
    log_section "Checking Environment Configuration"
    
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_success ".env file exists"
        
        # Check for critical API keys
        if grep -q "GEMINI_API_KEY" "$PROJECT_ROOT/.env"; then
            local key=$(grep "GEMINI_API_KEY" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
            if [ -z "$key" ] || [ "$key" = "your_gemini_api_key_here" ]; then
                log_warning "GEMINI_API_KEY is not set or is a placeholder"
            else
                log_success "GEMINI_API_KEY is configured"
            fi
        fi
        
        return 0
    else
        log_error ".env file not found"
        return 1
    fi
}

# ============================================================================
# Summary & Report
# ============================================================================

generate_report() {
    log_header "Health Check Summary"
    
    log_section "Service Endpoints"
    echo ""
    printf "%-25s %-40s\n" "Service" "URL/Port"
    echo "─────────────────────────────────────────────────────────────────"
    printf "%-25s %-40s\n" "Backend API" "http://localhost:8000"
    printf "%-25s %-40s\n" "Data Service API" "http://localhost:8001/docs"
    printf "%-25s %-40s\n" "AI Service (Streamlit)" "http://localhost:8501"
    printf "%-25s %-40s\n" "Frontend UI" "http://localhost:5173"
    printf "%-25s %-40s\n" "LocalStack (DynamoDB)" "http://localhost:4566"
    echo ""
    
    log_section "Next Steps"
    echo ""
    echo "1. Access the Frontend UI:"
    echo "   ${BLUE}http://localhost:5173${NC}"
    echo ""
    echo "2. Try the Data Service API:"
    echo "   ${BLUE}http://localhost:8001/docs${NC}"
    echo ""
    echo "3. Test the AI Service:"
    echo "   ${BLUE}http://localhost:8501${NC}"
    echo ""
    echo "4. View service logs:"
    echo "   ${BLUE}./main.sh logs${NC}"
    echo ""
    echo "5. Check service status anytime:"
    echo "   ${BLUE}./main.sh status${NC}"
    echo ""
}

# ============================================================================
# Main Function
# ============================================================================

main() {
    log_header "Stock Debate Advisor v6 - Health Check"
    
    local failed=0
    
    # Run checks
    check_docker_daemon || failed=1
    echo ""
    
    check_docker_compose || failed=1
    echo ""
    
    check_environment || failed=1
    echo ""
    
    if [ $failed -eq 0 ]; then
        check_containers || true
        echo ""
        
        check_database_services || true
        echo ""
        
        check_api_services || true
        echo ""
        
        check_frontend || true
        echo ""
        
        generate_report
        
        log_success "Health check completed!"
        return 0
    else
        log_error "Environment checks failed. Please run './main.sh start' first."
        return 1
    fi
}

# Run main
main "$@"
