# Stock Debate Advisor v7 - Minimal CDK Demo

A production-ready serverless demonstration of multi-agent AI stock analysis using AWS CDK.

## 🏗️ Architecture

```
v7/
├── cdk/                    # AWS CDK Infrastructure (TypeScript)
│   └── src/
│       ├── index.ts        # CDK App entry
│       └── stock-debate-stack.ts  # Main stack definition
├── ai-service/             # CrewAI Debate Orchestration (Lambda)
│   └── lambda/
│       ├── index.py        # Lambda handler
│       └── crew_agents.py  # Multi-agent implementation
├── data_store/             # Data Retrieval Service (Lambda)
│   └── lambda/
│       └── index.py        # Data fetch & cache handler
├── frontend/               # React SPA
│   └── src/
│       ├── App.tsx
│       └── components/     # Debate form & results
└── scripts/                # Deployment automation
```

## 🎯 Infrastructure Components

### AWS Services
- **API Gateway**: REST API with Cognito authorization
- **Lambda**: Serverless compute for debate & data services
- **DynamoDB**: Debate history & stock cache with TTL
- **Cognito**: User authentication
- **CloudFront + S3**: Frontend SPA hosting
- **Secrets Manager**: API key management

### Key Features
- Multi-agent debate using CrewAI
- Token-based authentication
- Real-time debate orchestration (15min timeout)
- Stock data caching with TTL
- Debate history tracking
- Serverless scaling

## 🚀 Quick Start

### Prerequisites
```bash
# Install AWS CLI and CDK
npm install -g aws-cdk
aws configure

# Install Node.js 18+ and npm
# Python 3.12 for Lambda layer
```

### 1. Deploy Infrastructure

```bash
cd cdk
npm install
npm run build

# Set environment variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Deploy CDK stack
npm run cdk:deploy
```

Output will show:
- API Gateway endpoint
- CloudFront frontend URL
- Cognito User Pool ID
- DynamoDB table names

### 2. Build Lambda Layers

```bash
cd ../lambda-layer
pip install -r requirements.txt -t python/lib/python3.12/site-packages/
# This creates the layer structure for CDK to package
```

### 3. Deploy Frontend

```bash
cd ../frontend
npm install
npm run build

# Upload to S3 (replace bucket name from CDK output)
aws s3 sync dist/ s3://stock-debate-frontend-dev-<account-id>/
```

### 4. Set Up Secrets

```bash
# Store Gemini API key in Secrets Manager
aws secretsmanager create-secret \
  --name gemini-api-key \
  --secret-string '{"api_key":"your-key-here"}'
```

### 5. Access Application

Open CloudFront URL from CDK outputs:
```
https://<cloudfront-domain>.cloudfront.net
```

## 📡 API Endpoints

### Create Debate
```bash
curl -X POST https://<api-domain>/debates \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MBB",
    "question": "Is this a good buy?",
    "userId": "user123"
  }'
```

Response:
```json
{
  "debateId": "debate-MBB-1705342800",
  "symbol": "MBB",
  "status": "completed",
  "result": {
    "output": "Multi-agent analysis..."
  }
}
```

### Get Debate Results
```bash
curl -X GET https://<api-domain>/debates?debateId=debate-MBB-1705342800 \
  -H "Authorization: Bearer <token>"
```

### Fetch Stock Data
```bash
curl https://<api-domain>/data/MBB
```

## 🔧 Development

### Local Testing

```bash
# Test AI Service Lambda locally
cd ai-service/lambda
python -m pytest test_lambda.py

# Test Data Service Lambda
cd data_store/lambda
python -m pytest test_lambda.py

# Test Frontend
cd frontend
npm test
```

### CDK Commands

```bash
cd cdk

# View infrastructure diff
npm run cdk:diff

# Synthesize CloudFormation
npm run cdk:synth

# Destroy stack
npm run cdk:destroy
```

## 📊 Monitoring

### CloudWatch Logs
```bash
# View Lambda logs
aws logs tail /aws/lambda/StockDebate-debate-orchestrator-dev --follow

# View API Gateway logs
aws logs tail /aws/apigateway/StockDebate-dev --follow
```

### DynamoDB Monitoring
```bash
# Monitor debates table
aws dynamodb describe-table --table-name StockDebate-debates-dev
```

## 🔐 Security

- **Encryption**: S3 (SSE-S3), DynamoDB encrypted
- **Access Control**: IAM roles, Cognito authentication
- **API Security**: CORS restricted, API Gateway authorization
- **Secrets**: API keys stored in Secrets Manager
- **CloudFront**: HTTPS enforced, caching headers

## 💰 Cost Estimate (Monthly)

- Lambda: ~$5-15 (depending on usage)
- DynamoDB: ~$5-10 (on-demand pricing)
- CloudFront: ~$1-5 (data transfer)
- API Gateway: ~$3-5
- **Total**: ~$15-35/month for dev environment

## 🚢 Production Deployment

1. Update `context` in `cdk/cdk.json` to `"environment": "prod"`
2. Enable Point-in-Time Recovery for DynamoDB
3. Set up CloudFront origin domain properly
4. Configure Cognito OAuth callbacks for production domain
5. Deploy to production region
6. Set up CloudWatch alarms

```bash
cd cdk
npm run cdk:deploy -- -c environment=prod
```

## 📚 References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Lambda Handler Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Cognito Authentication](https://docs.aws.amazon.com/cognito/)

## 📝 License

MIT License - See LICENSE file

## 🤝 Support

For issues or questions:
1. Check CloudWatch logs
2. Verify IAM permissions
3. Ensure Secrets Manager has API keys
4. Check DynamoDB table status

---

**Version**: v7.0.0
**Last Updated**: January 2025
