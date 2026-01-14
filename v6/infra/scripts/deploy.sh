#!/bin/bash
set -euo pipefail

# Deployment helper script for Stock Debate Advisor AWS CDK infrastructure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${ENVIRONMENT:-dev}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"
ACTION="${1:-help}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Check prerequisites
check_prerequisites() {
    local missing=0
    
    log_info "Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found"
        missing=1
    fi
    
    if ! command -v cdk &> /dev/null; then
        log_error "AWS CDK CLI not found"
        missing=1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found"
        missing=1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        log_error "Missing required prerequisites"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Install CDK dependencies
install_dependencies() {
    log_info "Installing CDK dependencies..."
    cd "$INFRA_DIR"
    npm install
    log_success "Dependencies installed"
}

# Lint TypeScript
lint_cdk() {
    log_info "Linting CDK infrastructure..."
    cd "$INFRA_DIR"
    npm run lint || log_warn "Linting failed (non-critical)"
    log_success "Linting complete"
}

# Build Docker images
build_docker_images() {
    log_info "Building Docker images..."
    
    local images=(
        "backend:latest"
        "data-service:latest"
        "ai-service:latest"
        "frontend:latest"
    )
    
    for image_spec in "${images[@]}"; do
        IFS=':' read -r service tag <<< "$image_spec"
        local dockerfile_path="$ROOT_DIR/$service/Dockerfile"
        
        if [ -f "$dockerfile_path" ]; then
            log_info "Building $service image..."
            docker build -t "stock-debate-$service:$tag" -f "$dockerfile_path" "$ROOT_DIR/$service"
            log_success "Built stock-debate-$service:$tag"
        else
            log_warn "Dockerfile not found for $service at $dockerfile_path"
        fi
    done
}

# Push images to ECR
push_to_ecr() {
    log_info "Pushing Docker images to ECR..."
    
    # Get account ID
    local account_id=$(aws sts get-caller-identity --query Account --output text --profile "$AWS_PROFILE")
    local ecr_uri="$account_id.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    log_info "ECR URI: $ecr_uri"
    
    # Login to ECR
    log_info "Logging in to ECR..."
    aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | \
        docker login --username AWS --password-stdin "$ecr_uri"
    
    local services=("backend" "data-service" "ai-service" "frontend")
    
    for service in "${services[@]}"; do
        local repo_name="stock-debate-$service"
        local local_image="$repo_name:latest"
        local remote_image="$ecr_uri/$repo_name:latest"
        
        # Tag image for ECR
        docker tag "$local_image" "$remote_image"
        
        # Push image
        log_info "Pushing $service to ECR..."
        docker push "$remote_image"
        log_success "Pushed $service to ECR"
    done
}

# Synthesize CDK
synth_cdk() {
    log_info "Synthesizing CDK infrastructure..."
    cd "$INFRA_DIR"
    cdk synth --profile "$AWS_PROFILE" --require-approval=never
    log_success "CDK synthesized"
}

# Deploy CDK stack
deploy_cdk() {
    log_info "Deploying CDK stack to AWS..."
    log_warn "Environment: $ENVIRONMENT, Region: $AWS_REGION"
    
    cd "$INFRA_DIR"
    cdk deploy \
        --profile "$AWS_PROFILE" \
        --require-approval=never \
        --context environment="$ENVIRONMENT" \
        --context aws_region="$AWS_REGION"
    
    log_success "CDK deployment complete"
}

# Destroy CDK stack
destroy_cdk() {
    log_warn "This will destroy all AWS resources for this stack!"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Destroy cancelled"
        return
    fi
    
    log_info "Destroying CDK stack..."
    cd "$INFRA_DIR"
    cdk destroy --profile "$AWS_PROFILE" --force
    log_success "Stack destroyed"
}

# List stack outputs
list_outputs() {
    log_info "Fetching stack outputs..."
    
    local stack_name="StockDebateStack-$ENVIRONMENT"
    
    aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Show help
show_help() {
    cat << EOF
${BLUE}Stock Debate Advisor - AWS CDK Deployment Script${NC}

Usage: $0 <action> [options]

Actions:
    help              Show this help message
    check             Check prerequisites
    install           Install CDK dependencies
    lint              Lint CDK infrastructure
    build-docker      Build Docker images locally
    push-ecr          Push images to AWS ECR
    synth             Synthesize CDK (generate CloudFormation)
    deploy            Deploy to AWS (builds + pushes + deploys)
    destroy           Destroy AWS stack
    outputs           Show stack outputs

Environment Variables:
    ENVIRONMENT       dev (default) or prod
    AWS_REGION        AWS region (default: us-east-1)
    AWS_PROFILE       AWS profile (default: default)

Examples:
    # Deploy to dev environment
    ENVIRONMENT=dev ./deploy.sh deploy
    
    # Deploy to prod environment  
    ENVIRONMENT=prod AWS_REGION=us-west-2 ./deploy.sh deploy
    
    # Just build Docker images
    ./deploy.sh build-docker
    
    # Check what would be deployed
    ./deploy.sh synth

EOF
}

# Main flow for full deployment
deploy_all() {
    log_info "Starting full deployment pipeline..."
    
    check_prerequisites
    install_dependencies
    lint_cdk
    build_docker_images
    push_to_ecr
    synth_cdk
    deploy_cdk
    
    log_success "Full deployment completed!"
    list_outputs
}

# Main script logic
case "$ACTION" in
    help)
        show_help
        ;;
    check)
        check_prerequisites
        ;;
    install)
        install_dependencies
        ;;
    lint)
        lint_cdk
        ;;
    build-docker)
        build_docker_images
        ;;
    push-ecr)
        push_to_ecr
        ;;
    synth)
        install_dependencies
        lint_cdk
        synth_cdk
        ;;
    deploy)
        deploy_all
        ;;
    destroy)
        destroy_cdk
        ;;
    outputs)
        list_outputs
        ;;
    *)
        log_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac
