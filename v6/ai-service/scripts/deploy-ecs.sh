#!/bin/bash
# ⚠️  REFERENCE SCRIPT - AWS deployment is managed via CDK infrastructure
# This script is for manual deployment and testing purposes only.
# For production deployment, use the CDK infrastructure:
#   cd ../infra && cdk deploy

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "⚠️  REFERENCE SCRIPT - For manual ECS deployment testing"
echo "✅ For production, use CDK: cd ../infra && cdk deploy"
echo ""
echo "🚀 Deploying Stock Debate Advisor AI Service to ECS Fargate"
echo "   Environment: $ENVIRONMENT"
echo "   Image Tag: $IMAGE_TAG"
echo "   AWS Region: $AWS_REGION"
echo "   AWS Account ID: $AWS_ACCOUNT_ID"

# Set image URI
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/stock-debate-ai-service:$IMAGE_TAG"

# 1. Build and push Docker image
echo ""
echo "📦 Building and pushing Docker image..."
docker build -t stock-debate-ai-service:$IMAGE_TAG .
docker tag stock-debate-ai-service:$IMAGE_TAG $IMAGE_URI

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Push image
docker push $IMAGE_URI
echo "✅ Image pushed to ECR: $IMAGE_URI"

# 2. Update ECS task definition
echo ""
echo "📝 Updating ECS task definition..."

# Replace placeholders in task definition
sed -e "s|YOUR_ECR_ACCOUNT_ID|$AWS_ACCOUNT_ID|g" \
    -e "s|YOUR_AWS_REGION|$AWS_REGION|g" \
    ecs-task-definition.json > /tmp/task-definition.json

# Register new task definition
TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-definition.json \
    --region $AWS_REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "✅ Task definition registered: $TASK_DEFINITION_ARN"

# 3. Update ECS service
echo ""
echo "🔄 Updating ECS service..."

SERVICE_NAME="stock-debate-ai-service-$ENVIRONMENT"
CLUSTER_NAME="stock-debate-$ENVIRONMENT"

aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $TASK_DEFINITION_ARN \
    --region $AWS_REGION \
    --force-new-deployment

echo "✅ Service updated: $SERVICE_NAME"

# 4. Wait for deployment to complete
echo ""
echo "⏳ Waiting for deployment to complete..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION

echo "✅ Deployment complete!"

# 5. Get service info
echo ""
echo "📊 Service Information:"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].[serviceName,status,runningCount,desiredCount]' \
    --output table

echo ""
echo "🎉 Stock Debate Advisor AI Service deployed successfully!"
echo ""
echo "📌 Note: For production deployments, use CDK infrastructure instead:"
echo "   cd ../infra && cdk deploy"
