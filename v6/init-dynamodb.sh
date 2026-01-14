#!/bin/bash

################################################################################
# Stock Debate Advisor v6 - LocalStack DynamoDB Initialization
#
# This script initializes DynamoDB tables in LocalStack for local development.
# It creates all necessary tables that would be deployed via CDK in production.
################################################################################

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# LocalStack endpoint
LOCALSTACK_ENDPOINT="http://localhost:4566"
AWS_REGION="us-east-1"

# AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="$AWS_REGION"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# Logging Functions
# ============================================================================

log_section() {
    echo -e "\n${BLUE}➜ $*${NC}"
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
# Helper Functions
# ============================================================================

wait_for_localstack() {
    log_info "Waiting for LocalStack to be ready..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$LOCALSTACK_ENDPOINT/health" > /dev/null 2>&1; then
            log_success "LocalStack is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    log_error "LocalStack failed to become ready"
    return 1
}

check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        log_info "Install with: pip install awscli-local"
        return 1
    fi
    
    if ! command -v awslocal &> /dev/null; then
        log_warning "awslocal is not installed, using aws with --endpoint-url"
    fi
    
    return 0
}

create_table() {
    local table_name=$1
    local key_schema=$2
    local attribute_definitions=$3
    local billing_mode=$4
    
    log_info "Creating table: $table_name"
    
    aws dynamodb create-table \
        --endpoint-url "$LOCALSTACK_ENDPOINT" \
        --table-name "$table_name" \
        --key-schema $key_schema \
        --attribute-definitions $attribute_definitions \
        --billing-mode "$billing_mode" \
        --region "$AWS_REGION" \
        2>/dev/null || {
        if grep -q "ResourceInUseException" <<< "$?"; then
            log_warning "Table $table_name already exists"
        else
            log_error "Failed to create table $table_name"
            return 1
        fi
    }
    
    log_success "Table $table_name created/verified"
    return 0
}

# ============================================================================
# Initialize DynamoDB Tables
# ============================================================================

init_tables() {
    log_section "Initializing DynamoDB Tables"
    
    # Companies table - stores company data
    create_table \
        "stock_debate-companies" \
        "AttributeName=symbol,KeyType=HASH" \
        "AttributeName=symbol,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # Stock prices table - stores historical price data
    create_table \
        "stock_debate-prices" \
        "AttributeName=symbol,KeyType=HASH AttributeName=date,KeyType=RANGE" \
        "AttributeName=symbol,AttributeType=S AttributeName=date,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # Financial data table - stores financial metrics
    create_table \
        "stock_debate-financials" \
        "AttributeName=symbol,KeyType=HASH AttributeName=quarter,KeyType=RANGE" \
        "AttributeName=symbol,AttributeType=S AttributeName=quarter,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # News articles table - stores news data
    create_table \
        "stock_debate-news" \
        "AttributeName=id,KeyType=HASH" \
        "AttributeName=id,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # Debates table - stores debate sessions
    create_table \
        "stock_debate-debates" \
        "AttributeName=debate_id,KeyType=HASH" \
        "AttributeName=debate_id,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # Analysis results table - stores analysis outputs
    create_table \
        "stock_debate-analysis" \
        "AttributeName=analysis_id,KeyType=HASH" \
        "AttributeName=timestamp,KeyType=RANGE" \
        "AttributeName=analysis_id,AttributeType=S AttributeName=timestamp,AttributeType=S" \
        "PAY_PER_REQUEST"
    
    # Sessions table - stores user sessions
    create_table \
        "stock_debate-sessions" \
        "AttributeName=session_id,KeyType=HASH" \
        "AttributeName=session_id,AttributeType=S" \
        "PAY_PER_REQUEST"
}

# ============================================================================
# List Tables
# ============================================================================

list_tables() {
    log_section "Existing DynamoDB Tables"
    
    echo ""
    aws dynamodb list-tables \
        --endpoint-url "$LOCALSTACK_ENDPOINT" \
        --region "$AWS_REGION" \
        --output table 2>/dev/null || true
    echo ""
}

# ============================================================================
# Main Function
# ============================================================================

main() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Stock Debate Advisor v6 - LocalStack DynamoDB Initialization${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check dependencies
    if ! check_aws_cli; then
        log_error "Missing dependencies"
        return 1
    fi
    
    # Wait for LocalStack
    if ! wait_for_localstack; then
        log_error "Cannot connect to LocalStack"
        log_info "Make sure LocalStack is running: ./main.sh start"
        return 1
    fi
    
    # Initialize tables
    if ! init_tables; then
        log_error "Failed to initialize tables"
        return 1
    fi
    
    # List tables
    list_tables
    
    log_success "DynamoDB initialization completed!"
    echo ""
}

main "$@"
