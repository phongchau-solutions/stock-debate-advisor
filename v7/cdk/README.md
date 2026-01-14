# AWS CDK Infrastructure - Stock Debate Advisor v7

AWS Cloud Development Kit (TypeScript) infrastructure for serverless stock debate platform.

## Overview

The CDK stack defines:
- **API Gateway**: REST API with Cognito authorization
- **Lambda Functions**: Debate orchestration & data loading
- **DynamoDB Tables**: Debate history & stock cache
- **Cognito**: User authentication
- **S3 + CloudFront**: Frontend SPA hosting
- **IAM Roles**: Least-privilege access

## Stack Structure

```typescript
StockDebateStack
├── Cognito
│   ├── UserPool (user-pool-${environment})
│   └── UserPoolClient
├── S3
│   └── Frontend Bucket (stock-debate-frontend-${environment}-${account})
├── CloudFront
│   ├── Distribution
│   ├── Origin Access Identity
│   └── Cache Policies
├── Lambda
│   ├── Debate Orchestrator (debate-orchestrator-${environment})
│   ├── Data Loader (data-loader-${environment})
│   └── Layer (shared-${environment})
├── DynamoDB
│   ├── Debates Table (debates-${environment})
│   │   ├── debateId (PK)
│   │   └── userIdIndex (GSI)
│   └── Stock Cache Table (stock-cache-${environment})
└── API Gateway
    ├── /debates (POST/GET)
    └── /data/{symbol} (GET)
```

## Development

### Prerequisites

```bash
# Install AWS CDK
npm install -g aws-cdk

# Verify installation
cdk --version
```

### Building

```bash
cd cdk

# Install dependencies
npm install

# Build TypeScript
npm run build

# View synthesis
npm run cdk:synth

# Compare with deployed
npm run cdk:diff
```

## Deployment

### First-Time Setup

```bash
# Configure AWS credentials
aws configure

# Get account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Verify AWS environment
aws ec2 describe-regions --query 'Regions[0].RegionName' --output text
```

### Deploy Stack

```bash
# Development deployment
npm run cdk:deploy

# Production deployment (with confirmation)
npm run cdk:deploy -- -c environment=prod
```

### Stack Outputs

After deployment, you'll see:
```
StockDebateFrontendURL = https://d1234.cloudfront.net
StockDebateAPIEndpoint = https://abcd1234.execute-api.us-east-1.amazonaws.com/prod/
StockDebateUserPoolId = us-east-1_xxxxx
StockDebateUserPoolClientId = 1234567890abcdef
StockDebateDebatesTableName = StockDebate-debates-dev
```

## Configuration

### Context Variables

In `cdk.json`:
```json
{
  "context": {
    "environment": "dev",
    "apiVersion": "v1",
    "stackPrefix": "StockDebate"
  }
}
```

### Environment Variables

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=123456789012
```

## Lambda Configuration

### Layer Dependencies

The CDK references a Lambda layer at `../lambda-layer/`:

```bash
# Build layer
cd ../lambda-layer
pip install -r requirements.txt -t python/lib/python3.12/site-packages/
```

### Lambda Environment

Debate Orchestrator receives:
```
DEBATES_TABLE = StockDebate-debates-${environment}
STOCK_CACHE_TABLE = StockDebate-stock-cache-${environment}
GEMINI_API_KEY = (from Secrets Manager)
ENVIRONMENT = dev|prod
```

Data Loader receives:
```
STOCK_CACHE_TABLE = StockDebate-stock-cache-${environment}
CACHE_TTL = 86400 (24 hours)
ENVIRONMENT = dev|prod
```

## DynamoDB Design

### Debates Table

**Partition Key**: `debateId` (String)
**Sort Key**: `timestamp` (Number)

Attributes:
- `userId`: String (for filtering by user)
- `symbol`: String (stock symbol)
- `question`: String (debate question)
- `result`: Map (debate output)
- `status`: String (completed|failed)
- `createdAt`: String (ISO 8601)

**GSI**: `userIdIndex`
- PK: `userId`
- SK: `timestamp`

### Stock Cache Table

**Partition Key**: `symbol` (String)

Attributes:
- `data`: Map (stock information)
- `ttl`: Number (Unix timestamp for auto-delete)
- `cached_at`: String (ISO 8601)

TTL is automatically managed - expired items are deleted after 24 hours.

## Security

### IAM Policies

**Debate Orchestrator Lambda**:
- DynamoDB: Read/Write to debates table
- DynamoDB: Read/Write to stock cache table
- Secrets Manager: Read gemini-api-key

**Data Loader Lambda**:
- DynamoDB: Read/Write to stock cache table

**CloudFront OAI**:
- S3: GetObject on frontend bucket

### API Authorization

- All `/debates` endpoints require Cognito authentication
- `/data/{symbol}` is public (no auth required)
- CORS headers configured for frontend domain

### Secrets Management

API keys stored in AWS Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name gemini-api-key \
  --secret-string '{"api_key":"your-key"}'
```

Lambda functions reference via:
```typescript
cdk.SecretValue.secretsManager('gemini-api-key', {
  jsonField: 'api_key'
})
```

## Monitoring & Logs

### CloudWatch Logs

Lambda logs available at:
```
/aws/lambda/StockDebate-debate-orchestrator-${environment}
/aws/lambda/StockDebate-data-loader-${environment}
```

View logs:
```bash
aws logs tail /aws/lambda/StockDebate-debate-orchestrator-dev --follow
```

### CloudWatch Metrics

Available metrics:
- Lambda invocations & duration
- Lambda errors & throttling
- DynamoDB read/write capacity
- API Gateway requests & latency

### X-Ray Tracing

Enable optional X-Ray tracing for deeper debugging:
```typescript
// Add to Lambda function
tracing: lambda.Tracing.ACTIVE
```

## Customization

### Add Lambda Function

```typescript
const myLambda = new lambda.Function(this, 'MyFunction', {
  functionName: `${stackPrefix}-my-function-${environment}`,
  runtime: lambda.Runtime.PYTHON_3_12,
  handler: 'index.handler',
  code: lambda.Code.fromAsset(path.join(__dirname, '../../my-service/lambda')),
  environment: {
    TABLE_NAME: myTable.tableName,
  },
});
```

### Add DynamoDB Table

```typescript
const myTable = new dynamodb.Table(this, 'MyTable', {
  tableName: `${stackPrefix}-my-table-${environment}`,
  partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
});
```

### Update API Routes

```typescript
const myResource = api.root.addResource('my-endpoint');
myResource.addMethod('GET', new apigateway.LambdaIntegration(myLambda));
```

## Maintenance

### Update Stack

```bash
# Make code changes
# Then:
npm run build
npm run cdk:diff    # Review changes
npm run cdk:deploy  # Apply changes
```

### Destroy Stack

```bash
npm run cdk:destroy
# or
aws cloudformation delete-stack --stack-name stock-debate-dev
```

**Warning**: Destroying the stack will delete DynamoDB tables and S3 buckets!

## Troubleshooting

### "Service role already exists"
→ CDK creates IAM roles automatically; existing ones cause conflicts
→ Solution: `cdk destroy` then `cdk deploy`

### "Lambda layer not found"
→ Build layer first: `cd ../lambda-layer && pip install -r requirements.txt -t python/lib/python3.12/site-packages/`

### "Secrets Manager permission denied"
→ Lambda execution role needs `secretsmanager:GetSecretValue` permission
→ Already included in CDK stack

### "API Gateway 403 Unauthorized"
→ Check Cognito User Pool client credentials
→ Ensure Authorization header has valid JWT token

## Performance

### Optimization Tips

1. **Lambda**: Use layers to reduce package size
2. **DynamoDB**: On-demand pricing avoids over-provisioning
3. **CloudFront**: Edge locations reduce latency
4. **S3**: CloudFront caches static assets

### Cold Start Mitigation

- Lambda: 512 MB+ memory for faster startup
- Layer: Dependencies pre-bundled
- Provisioned concurrency (production only)

## Cost Estimation

**Monthly costs** (dev environment):
- Lambda: ~$5-15
- DynamoDB: ~$5-10
- API Gateway: ~$3-5
- CloudFront: ~$1-5
- **Total**: ~$15-35

## References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Design Patterns](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Cognito Authentication](https://docs.aws.amazon.com/cognito/)
