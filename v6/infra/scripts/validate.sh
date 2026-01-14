#!/usr/bin/env bash
set -euo pipefail

# Infrastructure initialization and validation script
# Validates all infrastructure components are properly configured

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }

# Global validation state
VALIDATION_PASSED=0
VALIDATION_FAILED=0

# Validation functions
validate_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        log_success "$description exists: $file"
        ((VALIDATION_PASSED++))
    else
        log_error "$description missing: $file"
        ((VALIDATION_FAILED++))
    fi
}

validate_docker() {
    local service=$1
    local dockerfile="$PROJECT_ROOT/$service/Dockerfile"
    
    if [ -f "$dockerfile" ]; then
        # Check for multi-stage, non-root user, health check
        if grep -q "FROM.*as builder" "$dockerfile" 2>/dev/null || grep -q "FROM.*as builder" "$dockerfile" 2>/dev/null; then
            log_success "$service has multi-stage build"
        else
            log_warn "$service could benefit from multi-stage build"
        fi
        
        if grep -q "USER.*appuser\|USER.*nodejs" "$dockerfile"; then
            log_success "$service runs as non-root user"
            ((VALIDATION_PASSED++))
        else
            log_warn "$service missing non-root user setup"
            ((VALIDATION_FAILED++))
        fi
        
        if grep -q "HEALTHCHECK" "$dockerfile"; then
            log_success "$service has health check configured"
            ((VALIDATION_PASSED++))
        else
            log_warn "$service missing HEALTHCHECK directive"
            ((VALIDATION_FAILED++))
        fi
    else
        log_error "$service Dockerfile not found: $dockerfile"
        ((VALIDATION_FAILED++))
    fi
}

validate_npm_packages() {
    local package_json="$1"
    local required_packages=("aws-cdk-lib" "constructs")
    
    if [ ! -f "$package_json" ]; then
        log_error "package.json not found: $package_json"
        ((VALIDATION_FAILED++))
        return
    fi
    
    for package in "${required_packages[@]}"; do
        if grep -q "\"$package\"" "$package_json"; then
            log_success "npm package found: $package"
            ((VALIDATION_PASSED++))
        else
            log_error "npm package missing: $package"
            ((VALIDATION_FAILED++))
        fi
    done
}

# Main validation
main() {
    echo -e "${BLUE}==================== Infrastructure Validation ====================${NC}"
    echo ""
    
    # 1. CDK Files
    echo -e "${BLUE}Checking CDK Files...${NC}"
    validate_file "$PROJECT_ROOT/infra/bin/stock-debate-advisor.ts" "CDK entry point"
    validate_file "$PROJECT_ROOT/infra/lib/stock-debate-stack.ts" "Main CDK stack"
    validate_file "$PROJECT_ROOT/infra/ecs/task-definitions.ts" "ECS task definitions"
    validate_file "$PROJECT_ROOT/infra/ecs/services.ts" "ECS services"
    echo ""
    
    # 2. Configuration Files
    echo -e "${BLUE}Checking Configuration Files...${NC}"
    validate_file "$PROJECT_ROOT/infra/cdk.json" "CDK configuration"
    validate_file "$PROJECT_ROOT/infra/tsconfig.json" "TypeScript configuration"
    validate_file "$PROJECT_ROOT/infra/package.json" "NPM dependencies"
    echo ""
    
    # 3. Scripts
    echo -e "${BLUE}Checking Deployment Scripts...${NC}"
    validate_file "$PROJECT_ROOT/infra/scripts/deploy.sh" "Deployment script"
    validate_file "$PROJECT_ROOT/infra/scripts/local-setup.sh" "Local setup script"
    validate_file "$PROJECT_ROOT/Makefile" "Makefile"
    echo ""
    
    # 4. Docker Images
    echo -e "${BLUE}Checking Docker Images...${NC}"
    validate_docker "backend"
    validate_docker "data-service"
    validate_docker "ai-service"
    validate_docker "frontend"
    echo ""
    
    # 5. NPM Packages
    echo -e "${BLUE}Checking CDK Dependencies...${NC}"
    validate_npm_packages "$PROJECT_ROOT/infra/package.json"
    echo ""
    
    # 6. docker-compose
    echo -e "${BLUE}Checking Local Development Setup...${NC}"
    validate_file "$PROJECT_ROOT/docker-compose.yml" "Docker Compose"
    echo ""
    
    # Summary
    echo -e "${BLUE}==================== Validation Summary ====================${NC}"
    echo -e "Passed: ${GREEN}${VALIDATION_PASSED}${NC}"
    echo -e "Failed: ${RED}${VALIDATION_FAILED}${NC}"
    echo ""
    
    if [ $VALIDATION_FAILED -eq 0 ]; then
        log_success "All infrastructure components validated!"
        echo ""
        echo "Next steps:"
        echo "  1. Local Development:"
        echo "     make local-start        # Start services locally"
        echo "     make local-logs         # View logs"
        echo ""
        echo "  2. AWS Deployment:"
        echo "     make cdk-bootstrap      # First time only"
        echo "     make deploy             # Deploy to AWS"
        echo "     make outputs            # View deployment outputs"
        echo ""
        return 0
    else
        log_error "Infrastructure validation failed!"
        return 1
    fi
}

main "$@"
