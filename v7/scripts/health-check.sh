#!/bin/bash
# Health check script for Stock Debate Advisor v7
# Run periodically to monitor infrastructure

set -e

ENVIRONMENT=${1:-dev}
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="stock-debate-${ENVIRONMENT}"

echo "🏥 Health Check - Stock Debate Advisor v7"
echo "=========================================="
echo ""

# Check CDK Stack
echo "📚 CDK Stack Status:"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].[StackName,StackStatus]' \
  --output table

# Check Lambda Functions
echo ""
echo "⚡ Lambda Functions:"
aws lambda list-functions \
  --query "Functions[?contains(FunctionName, 'StockDebate')].{Name:FunctionName,Runtime:Runtime,Memory:MemorySize}" \
  --region "$REGION" \
  --output table

# Check DynamoDB Tables
echo ""
echo "🗄️ DynamoDB Tables:"
aws dynamodb list-tables \
  --query "TableNames[?contains(@, 'StockDebate')]" \
  --region "$REGION" \
  --output text | tr '\t' '\n'

# Check API Gateway
echo ""
echo "🔌 API Gateway:"
aws apigateway get-rest-apis \
  --query "items[?contains(name, 'StockDebate')].{Name:name,Status:status}" \
  --region "$REGION" \
  --output table

# Check CloudFront
echo ""
echo "🌍 CloudFront Distributions:"
aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Comment, 'StockDebate')].{Id:Id,Status:Status,DomainName:DomainName}" \
  --output table

# Check S3 Buckets
echo ""
echo "📦 S3 Buckets:"
aws s3 ls | grep stock-debate || echo "No S3 buckets found"

# Lambda Performance
echo ""
echo "📊 Lambda Recent Invocations (Last Hour):"
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/StockDebate-debate-orchestrator-${ENVIRONMENT}" \
  --region "$REGION" \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --query 'logStreams[0].[logStreamName,lastEventTimestamp]' || echo "No recent invocations"

echo ""
echo "✅ Health check complete!"
echo ""
echo "To view detailed logs:"
echo "  make logs"
echo ""
echo "To see full stack details:"
echo "  aws cloudformation describe-stacks --stack-name $STACK_NAME"
