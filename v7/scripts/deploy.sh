#!/bin/bash
set -e

echo "🚀 Stock Debate Advisor v7 - Deployment Script"
echo "=================================================="

# Check prerequisites
echo "✓ Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required"; exit 1; }

# Get AWS info
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo "✓ AWS Account: $AWS_ACCOUNT"
echo "✓ AWS Region: $AWS_REGION"

# Set environment
export AWS_ACCOUNT_ID=$AWS_ACCOUNT

# Build CDK
echo ""
echo "📦 Building CDK Stack..."
cd cdk
npm install --omit=dev
npm run build

# Synth CloudFormation
echo "✓ Synthesizing CloudFormation..."
npm run cdk:synth

# Deploy
echo ""
echo "🚀 Deploying to AWS..."
npm run cdk:deploy

# Get outputs
echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Stack Outputs:"
aws cloudformation describe-stacks \
  --stack-name stock-debate-dev \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs' \
  --output table

echo ""
echo "Next steps:"
echo "1. Store Gemini API key in Secrets Manager"
echo "2. Build and deploy frontend"
echo "3. Open the CloudFront URL in your browser"
