#!/bin/bash
# Stock Debate Advisor v7 - AWS CDK Deployment Script
# Automates the full deployment process

set -e

COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_step() {
    echo -e "${COLOR_BLUE}=== $1 ===${NC}"
}

log_success() {
    echo -e "${COLOR_GREEN}✓ $1${NC}"
}

log_warn() {
    echo -e "${COLOR_YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${COLOR_RED}✗ $1${NC}"
}

# Check prerequisites
log_step "Checking prerequisites"

if ! command -v aws &> /dev/null; then
    log_error "AWS CLI not found. Please install it first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    log_error "Node.js not found. Please install it first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    log_error "npm not found. Please install it first."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    log_warn "Docker not found. Lambda bundling might fail."
fi

log_success "All prerequisites met"

# Get AWS account and region
log_step "Retrieving AWS configuration"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}
log_success "AWS Account: $AWS_ACCOUNT, Region: $AWS_REGION"

# Step 1: Build Frontend
log_step "Building frontend"
cd "$(dirname "$0")/../frontend"
npm install > /dev/null 2>&1
npm run build > /dev/null 2>&1
log_success "Frontend built to dist/"
cd "$(dirname "$0")/.."

# Step 2: Setup CDK
log_step "Setting up CDK"
cd "$(dirname "$0")/../cdk"
npm install > /dev/null 2>&1

# Bootstrap if needed
log_step "Bootstrapping CDK environment"
npx cdk bootstrap aws://$AWS_ACCOUNT/$AWS_REGION --require-approval=never || true
log_success "CDK bootstrap complete"

# Step 3: Deploy stacks
log_step "Deploying CloudFormation stacks"
log_warn "This may take 10-15 minutes..."

npx cdk deploy --all --require-approval=never

# Step 4: Get outputs
log_step "Retrieving deployment outputs"

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name stock-debate-advisor-compute-prod \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name stock-debate-advisor-frontend-prod \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DistributionUrl`].OutputValue' \
    --output text)

COMPANIES_TABLE=$(aws cloudformation describe-stacks \
    --stack-name stock-debate-advisor-data-prod \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CompaniesTableName`].OutputValue' \
    --output text)

# Step 5: Test API
log_step "Testing API endpoints"

HEALTH_RESPONSE=$(curl -s $API_ENDPOINT/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    log_success "Health check passed: $API_ENDPOINT/health"
else
    log_error "Health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Step 6: Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Stock Debate Advisor v7 Deployed Successfully        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 API Endpoint:    $API_ENDPOINT"
echo "🌐 Frontend URL:    $FRONTEND_URL"
echo "📊 Data Tables:     DynamoDB (companies, financial_reports, ohlc_prices, debate_results)"
echo ""
echo "✅ Next steps:"
echo "   1. Enable Bedrock Claude 3 Sonnet model in AWS Console"
echo "   2. Migrate stock data: aws lambda invoke --function-name stock-debate-advisor-DataMigration-* --payload '{\"action\":\"migrate_from_s3\"}' /tmp/result.json"
echo "   3. Visit frontend: $FRONTEND_URL"
echo "   4. Test debate API: curl -X POST $API_ENDPOINT/debate -H 'Content-Type: application/json' -d '{\"ticker\":\"MBB\",\"timeframe\":\"1d\"}'"
echo ""
echo "📚 Full guide: See DEPLOYMENT_CDK.md"
echo ""

cd ../..
