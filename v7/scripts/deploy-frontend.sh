#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}
BUCKET_NAME="stock-debate-frontend-${ENVIRONMENT}-$(aws sts get-caller-identity --query Account --output text)"

echo "📦 Building Frontend..."
cd frontend
npm install
npm run build

echo "📤 Uploading to S3..."
aws s3 sync dist/ "s3://${BUCKET_NAME}/" \
  --delete \
  --cache-control "max-age=604800" \
  --exclude "index.html"

# Set index.html to not cache
aws s3 cp dist/index.html "s3://${BUCKET_NAME}/index.html" \
  --cache-control "max-age=0" \
  --content-type "text/html"

echo "✅ Frontend Deployed!"
echo ""
echo "CloudFront URL from CDK outputs:"
aws cloudformation describe-stacks \
  --stack-name "stock-debate-${ENVIRONMENT}" \
  --query 'Stacks[0].Outputs[?OutputKey==`StockDebateFrontendURL`].[OutputValue]' \
  --output text
