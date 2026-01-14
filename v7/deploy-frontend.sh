#!/bin/bash
# V7 Build and Deploy Frontend to S3
# Similar to Cecchetti Dashboard

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
S3_BUCKET="${S3_BUCKET:-stock-debate-frontend}"
AWS_REGION="${AWS_REGION:-us-east-1}"
CLOUDFRONT_DIST_ID="${CLOUDFRONT_DIST_ID:-}"

echo -e "${YELLOW}📦 Building Frontend for Production${NC}"
echo "Bucket: $S3_BUCKET"
echo "Region: $AWS_REGION"
echo ""

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d node_modules ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Build
echo -e "${YELLOW}Building...${NC}"
npm run build

if [ ! -d dist ]; then
    echo -e "${RED}❌ Build failed - dist directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# Upload to S3
echo -e "${YELLOW}📤 Uploading to S3: s3://$S3_BUCKET${NC}"

# Sync dist folder to S3 (with cache busting for assets)
aws s3 sync dist "s3://$S3_BUCKET" \
    --region "$AWS_REGION" \
    --delete \
    --cache-control "public, max-age=3600" \
    --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp dist/index.html "s3://$S3_BUCKET/index.html" \
    --region "$AWS_REGION" \
    --cache-control "public, max-age=0, must-revalidate" \
    --content-type "text/html"

echo -e "${GREEN}✅ Upload complete${NC}"

# Invalidate CloudFront if dist ID provided
if [ -n "$CLOUDFRONT_DIST_ID" ]; then
    echo -e "${YELLOW}🔄 Invalidating CloudFront cache...${NC}"
    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DIST_ID" \
        --paths "/*" \
        --region "$AWS_REGION"
    echo -e "${GREEN}✅ CloudFront invalidated${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo "Frontend URL: https://$S3_BUCKET.s3.$AWS_REGION.amazonaws.com"
