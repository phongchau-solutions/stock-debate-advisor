#!/bin/bash
set -e

echo "🧹 Cleaning up v7 deployment..."

ENVIRONMENT=${1:-dev}
STACK_NAME="stock-debate-${ENVIRONMENT}"

# Confirm
read -p "Are you sure you want to delete the stack? (yes/no) " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo "Destroying CDK stack: $STACK_NAME"
cd cdk
npm run cdk:destroy

echo "✅ Stack destroyed"
echo "Note: S3 buckets and DynamoDB tables may need manual cleanup if deletion protection is enabled"
