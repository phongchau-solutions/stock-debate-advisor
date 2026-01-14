#!/bin/bash
# ⚠️  REFERENCE SCRIPT - AWS deployment is managed via CDK infrastructure
# This script is for manual Lambda deployment testing purposes only.
# For production deployment, use the CDK infrastructure:
#   cd ../infra && cdk deploy

set -e

ENVIRONMENT=${1:-staging}
AWS_REGION=${AWS_REGION:-us-east-1}
LAMBDA_FUNCTION_NAME="stock-debate-ai-service-$ENVIRONMENT"

echo "⚠️  REFERENCE SCRIPT - For manual Lambda deployment testing"
echo "✅ For production, use CDK: cd ../infra && cdk deploy"
echo ""
echo "🚀 Deploying Stock Debate Advisor AI Service to AWS Lambda"
echo "   Environment: $ENVIRONMENT"
echo "   AWS Region: $AWS_REGION"
echo "   Function Name: $LAMBDA_FUNCTION_NAME"

# 1. Build deployment package
echo ""
echo "📦 Building Lambda deployment package..."

mkdir -p lambda_package
cd lambda_package
pip install -r ../requirements.txt -t .
cp -r ../*.py .
cd ..

zip -r lambda_deployment.zip lambda_package/

echo "✅ Deployment package created: lambda_deployment.zip"

# 2. Create or update Lambda function
echo ""
echo "⚙️ Creating/updating Lambda function..."

# Check if function exists
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "   Updating existing function..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb://lambda_deployment.zip \
        --region $AWS_REGION
else
    echo "   Creating new function..."
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --runtime python3.11 \
        --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
        --handler main.lambda_handler \
        --zip-file fileb://lambda_deployment.zip \
        --timeout 900 \
        --memory-size 2048 \
        --environment Variables="{CREWAI_MODEL=gemini-2.5-pro,CREW_VERBOSE=True,CREW_MEMORY=True}" \
        --region $AWS_REGION
fi

echo "✅ Lambda function ready: $LAMBDA_FUNCTION_NAME"

# 3. Create/update API Gateway
echo ""
echo "🌐 Setting up API Gateway..."

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $AWS_REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "   Lambda ARN: $LAMBDA_ARN"

# Note: Manual API Gateway setup or use serverless framework is recommended
echo "⚠️  Manual API Gateway setup required. Use AWS Console or serverless framework."
echo "   Lambda Function ARN: $LAMBDA_ARN"

# 4. Cleanup
echo ""
echo "🧹 Cleaning up..."
rm -rf lambda_package
rm lambda_deployment.zip

echo ""
echo "🎉 Stock Debate Advisor AI Service deployed to Lambda!"
echo "   Next steps:"
echo "   1. Create API Gateway endpoints pointing to $LAMBDA_FUNCTION_NAME"
echo "   2. Test with: aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION response.json && cat response.json"
