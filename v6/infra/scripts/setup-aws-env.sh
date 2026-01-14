#!/bin/bash
set -euo pipefail

# AWS Environment Setup Script
# Sets up all necessary AWS resources and configurations for deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }

# Get AWS Account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text --profile "$AWS_PROFILE"
}

# Create S3 bucket for CDK assets
setup_cdk_assets_bucket() {
    local account_id=$(get_account_id)
    local bucket_name="cdk-assets-$account_id-$AWS_REGION"
    
    log_info "Setting up CDK assets bucket: $bucket_name"
    
    if aws s3 ls "s3://$bucket_name" --profile "$AWS_PROFILE" 2>/dev/null; then
        log_success "CDK assets bucket already exists"
    else
        log_info "Creating CDK assets bucket..."
        aws s3 mb "s3://$bucket_name" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$bucket_name" \
            --versioning-configuration Status=Enabled \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE"
        
        log_success "CDK assets bucket created"
    fi
}

# Create IAM role for GitHub Actions
setup_github_actions_role() {
    log_info "Setting up GitHub Actions IAM role..."
    
    local role_name="GitHubActionsDeployRole"
    local account_id=$(get_account_id)
    local github_org="${GITHUB_ORG:-}"
    local github_repo="${GITHUB_REPO:-stock-debate-advisor}"
    
    # Check if role exists
    if aws iam get-role --role-name "$role_name" --profile "$AWS_PROFILE" 2>/dev/null; then
        log_success "GitHub Actions role already exists"
        return
    fi
    
    log_warn "GitHub_ORG not set, skipping role creation"
    log_info "To create GitHub Actions role, run:"
    echo "  GITHUB_ORG=<org> GITHUB_REPO=<repo> bash $0"
    
    # Trust policy
    local trust_policy='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::'$account_id':oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:'$github_org'/'$github_repo':*"
        }
      }
    }
  ]
}'
    
    # Create role
    aws iam create-role \
        --role-name "$role_name" \
        --assume-role-policy-document "$trust_policy" \
        --profile "$AWS_PROFILE"
    
    # Attach policies
    aws iam attach-role-policy \
        --role-name "$role_name" \
        --policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
        --profile "$AWS_PROFILE"
    
    log_success "GitHub Actions role created"
}

# Create secrets for GitHub Actions
setup_github_secrets() {
    log_info "GitHub Actions secrets setup:"
    
    local account_id=$(get_account_id)
    local role_arn="arn:aws:iam::$account_id:role/GitHubActionsDeployRole"
    
    echo ""
    echo "Add these secrets to your GitHub repository:"
    echo ""
    echo "  AWS_ACCOUNT_ID:"
    echo "    $account_id"
    echo ""
    echo "  AWS_ROLE_TO_ASSUME:"
    echo "    $role_arn"
    echo ""
    echo "  SLACK_WEBHOOK (optional):"
    echo "    https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    echo ""
}

# Create ECR repositories
setup_ecr_repositories() {
    log_info "Setting up ECR repositories..."
    
    local repositories=("backend" "data-service" "ai-service" "frontend")
    
    for repo in "${repositories[@]}"; do
        local repo_name="stock-debate-$repo"
        
        if aws ecr describe-repositories \
            --repository-names "$repo_name" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" 2>/dev/null; then
            log_success "ECR repository already exists: $repo_name"
        else
            log_info "Creating ECR repository: $repo_name"
            
            aws ecr create-repository \
                --repository-name "$repo_name" \
                --image-scanning-configuration scanOnPush=true \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE"
            
            log_success "Created ECR repository: $repo_name"
        fi
    done
}

# Create KMS key for encryption
setup_kms_key() {
    log_info "Setting up KMS key for encryption..."
    
    local key_description="Stock Debate Advisor encryption key"
    
    # Check if key already exists by description
    local key_id=$(aws kms list-keys --region "$AWS_REGION" --profile "$AWS_PROFILE" \
        --query 'Keys[0].KeyId' --output text 2>/dev/null || echo "")
    
    if [ -z "$key_id" ]; then
        log_info "Creating KMS key..."
        
        key_id=$(aws kms create-key \
            --description "$key_description" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --query 'KeyMetadata.KeyId' \
            --output text)
        
        log_success "Created KMS key: $key_id"
    else
        log_success "KMS key already exists: $key_id"
    fi
}

# Create VPC endpoints for private services
setup_vpc_endpoints() {
    log_info "VPC endpoints configuration:"
    echo ""
    echo "The main CDK stack will create VPC endpoints for:"
    echo "  - ECR API"
    echo "  - ECR DKR (Docker)"
    echo "  - CloudWatch Logs"
    echo "  - Secrets Manager"
    echo "  - S3 Gateway"
    echo ""
}

# Configure AWS CLI
setup_aws_cli() {
    log_info "Validating AWS CLI configuration..."
    
    # Test credentials
    if ! aws sts get-caller-identity --profile "$AWS_PROFILE" &>/dev/null; then
        log_error "AWS credentials invalid for profile: $AWS_PROFILE"
        log_info "Run: aws configure --profile $AWS_PROFILE"
        return 1
    fi
    
    log_success "AWS CLI configured correctly"
    
    # Show account info
    local account_id=$(get_account_id)
    local user=$(aws iam get-user --profile "$AWS_PROFILE" --query 'User.UserName' --output text 2>/dev/null || echo "assume-role")
    
    echo ""
    echo "Connected as:"
    echo "  Account: $account_id"
    echo "  User/Role: $user"
    echo "  Region: $AWS_REGION"
    echo ""
}

# Create environment file
create_env_file() {
    log_info "Creating .env file for infrastructure..."
    
    local account_id=$(get_account_id)
    
    cat > "$PROJECT_ROOT/infra/.env" << EOF
# AWS Configuration
AWS_ACCOUNT_ID=$account_id
AWS_REGION=$AWS_REGION
AWS_PROFILE=$AWS_PROFILE

# Environment
ENVIRONMENT=$ENVIRONMENT

# GitHub Configuration (for CI/CD)
GITHUB_ORG=
GITHUB_REPO=stock-debate-advisor

# Slack Configuration (for notifications)
SLACK_WEBHOOK=

# Database
DB_USER=postgres
DB_NAME=stock_debate
DB_BACKUP_RETENTION_DAYS=$([[ "$ENVIRONMENT" == "prod" ]] && echo "30" || echo "7")

# Domain (configure after deployment)
DOMAIN_NAME=
CERTIFICATE_ARN=
EOF
    
    log_success "Created .env file: infra/.env"
    echo ""
    echo "Edit this file with your specific values:"
    echo "  $PROJECT_ROOT/infra/.env"
}

# Main menu
main() {
    echo -e "${BLUE}========== AWS Environment Setup ==========${NC}"
    echo ""
    echo "Region: $AWS_REGION"
    echo "Profile: $AWS_PROFILE"
    echo "Environment: $ENVIRONMENT"
    echo ""
    
    # Run setup steps
    setup_aws_cli || return 1
    setup_cdk_assets_bucket
    setup_ecr_repositories
    setup_kms_key
    setup_vpc_endpoints
    setup_github_actions_role
    setup_github_secrets
    create_env_file
    
    echo -e "${BLUE}========== Setup Complete ==========${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review and update: infra/.env"
    echo "  2. Run validation: bash infra/scripts/validate.sh"
    echo "  3. Bootstrap CDK: make cdk-bootstrap"
    echo "  4. Deploy: make deploy"
    echo ""
}

main "$@"
