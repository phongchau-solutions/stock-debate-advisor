#!/bin/bash
set -euo pipefail

# Quick start script - Sets up and deploys Stock Debate Advisor
# Handles the full pipeline: local setup → validation → deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }
log_header() { echo -e "\n${BLUE}===== $* =====${NC}\n"; }

# Get user choice
read_choice() {
    local prompt=$1
    local choice
    read -p "$(echo -e ${BLUE}$prompt${NC})" choice
    echo "$choice"
}

main() {
    clear
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         Stock Debate Advisor - Quick Start               ║
║                                                           ║
║    Seamless AWS Deployment Infrastructure Setup          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo ""
    
    log_header "Choose Deployment Option"
    
    echo "1) Local Development (docker-compose)"
    echo "2) Deploy to AWS"
    echo "3) Validate Infrastructure"
    echo "4) View Documentation"
    echo "5) Exit"
    echo ""
    
    local choice=$(read_choice "Select option (1-5): ")
    
    case "$choice" in
        1)
            deploy_local
            ;;
        2)
            deploy_aws
            ;;
        3)
            validate_infrastructure
            ;;
        4)
            show_documentation
            ;;
        5)
            log_info "Exiting"
            exit 0
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
}

deploy_local() {
    log_header "Local Development Setup"
    
    log_info "Starting all services locally..."
    log_info "This uses docker-compose to run the full stack"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    log_success "Services starting..."
    sleep 5
    
    docker-compose ps
    
    echo ""
    log_success "Local deployment ready!"
    echo ""
    echo "Access services at:"
    echo "  Backend:      http://localhost:8000"
    echo "  Data Service: http://localhost:8001"
    echo "  AI Service:   http://localhost:8501"
    echo "  Frontend:     http://localhost:5173"
    echo ""
    echo "Useful commands:"
    echo "  make local-logs [SERVICE=backend]  - View logs"
    echo "  make local-stop                    - Stop services"
    echo "  make local-clean                   - Remove containers"
    echo ""
}

deploy_aws() {
    log_header "AWS Deployment"
    
    echo "Deployment targets:"
    echo "1) Development (dev)"
    echo "2) Production (prod)"
    echo "3) Back to main menu"
    echo ""
    
    local env=$(read_choice "Select environment (1-3): ")
    
    case "$env" in
        1)
            environment="dev"
            ;;
        2)
            environment="prod"
            ;;
        3)
            main
            return
            ;;
        *)
            log_error "Invalid option"
            return
            ;;
    esac
    
    log_info "Deploying to $environment environment..."
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not installed"
        echo "Install from: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    if ! command -v cdk &> /dev/null; then
        log_error "AWS CDK not installed"
        log_info "Installing: npm install -g aws-cdk"
        npm install -g aws-cdk || exit 1
    fi
    
    # Setup AWS environment if needed
    if [ ! -f "$PROJECT_ROOT/infra/.env" ]; then
        log_info "Running AWS environment setup..."
        bash "$PROJECT_ROOT/infra/scripts/setup-aws-env.sh" || exit 1
    fi
    
    # Bootstrap if needed
    log_info "Bootstrapping CDK..."
    cd "$PROJECT_ROOT/infra"
    
    if ! cdk bootstrap 2>/dev/null; then
        log_warn "CDK bootstrap may require user confirmation"
        cdk bootstrap --require-approval=always || true
    fi
    
    # Deploy
    log_info "Starting deployment pipeline..."
    echo ""
    
    cd "$PROJECT_ROOT"
    ENVIRONMENT="$environment" make deploy || exit 1
    
    log_success "Deployment complete!"
    
    # Show outputs
    echo ""
    log_info "Stack outputs:"
    ENVIRONMENT="$environment" make outputs
    echo ""
}

validate_infrastructure() {
    log_header "Validating Infrastructure"
    
    bash "$PROJECT_ROOT/infra/scripts/validate.sh"
}

show_documentation() {
    log_header "Documentation"
    
    echo "Available documentation:"
    echo ""
    echo "1) Infrastructure Guide"
    echo "   → $PROJECT_ROOT/infra/README.md"
    echo ""
    echo "2) Infrastructure Summary"
    echo "   → $PROJECT_ROOT/INFRASTRUCTURE.md"
    echo ""
    echo "3) Project README"
    echo "   → $PROJECT_ROOT/README.md"
    echo ""
    echo "4) View Makefile targets"
    echo "   → make help"
    echo ""
    
    echo "Key sections:"
    echo "  • Quick Start"
    echo "  • Architecture Overview"
    echo "  • Deployment Guide"
    echo "  • Troubleshooting"
    echo "  • Cost Optimization"
    echo ""
}

# Run interactive menu
main
