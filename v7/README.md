# Stock Debate Advisor v7 - Production-Ready Serverless AI

A production-ready serverless system for multi-agent AI stock analysis debates using AWS services and AWS Bedrock Claude.

## 🎯 Key Improvements (Jan 2024)

✅ **Fixed Frontend API Endpoint** - No longer hardcoded to localhost; uses deployed API Gateway
✅ **Long-Running Debate Support** - ECS Fargate handles debates >15 minutes (Lambda limit)  
✅ **Professional Backend Services** - Modular Python services for code reuse, security, and testability

## 🏗️ System Architecture

```
┌─────────────────────────────┐
│   Frontend (React SPA)       │
│   S3 + CloudFront (HTTPS)    │
└────────────┬────────────────┘
             │ /api/* proxy
             ↓
┌─────────────────────────────┐
│   API Gateway (REST)        │
│   CORS + Throttling + Logging
└──────┬────────────────┬─────┘
       │                │
   /health          /debate (POST)
       │                │
       ▼                ▼
   [LAMBDA]        [LAMBDA WRAPPER]
   (Health)        (Submit Task → SQS)
   (30s timeout)   (returns 202 Accepted)
                        │
                        ↓
                    [SQS QUEUE]
                   (Debate Tasks)
                        │
                        ↓ consume
            ┌───────────────────────┐
            │  ECS Fargate Cluster  │
            │  (Auto-scale 1-10)    │
            │  15-min timeout/task  │
            │                       │
            │  Multi-agent debate:  │
            │  - Fundamental Agent  │
            │  - Technical Agent    │
            │  - Sentiment Agent    │
            │  - Judge Agent        │
            └───────┬───────────────┘
                    │
                    ↓
        ┌──────────────────────────┐
        │  BACKEND SERVICES        │
        │  (Modular Python)        │
        │                          │
        │  - Orchestrator (Debate) │
        │  - DataService (Data)    │
        │  - Database (DynamoDB)   │
        └───────┬──────────────────┘
                │
                ↓
    ┌──────────────────────────────┐
    │  AWS Bedrock (Claude 3.5)    │
    │  AWS DynamoDB (Results)      │
    └──────────────────────────────┘
```

## 🚀 Quick Deploy (2 commands)

### Prerequisites
```bash
# Configure AWS credentials once
aws configure
```

### Build & Deploy
```bash
# Build frontend
cd v7/frontend && npm install && npm run build

# Deploy infrastructure
cd ../cdk && npm install
USE_ECS_DEBATES=true cdk deploy --all --require-approval never
```

This deploys in ~10 minutes with:
- Lambda functions (health, API wrapper)
- ECS Fargate cluster (long-running debates)
- SQS queue (async task distribution)
- DynamoDB tables (data storage)
- S3 + CloudFront (frontend hosting)
- API Gateway (REST endpoints)

### Get URLs
```bash
aws cloudformation describe-stacks \
  --stack-name stock-debate-advisor-frontend-prod \
  --query 'Stacks[0].Outputs' --output table
```

## 📚 Project Structure

```
v7/
├── frontend/                # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── api/            # API client services
│   │   ├── components/     # React components
│   │   └── App.tsx         # Main app
│   ├── .env.production     # Production config template
│   └── vite.config.ts      # Build configuration
│
├── backend/                # NEW: Modular Python services
│   ├── models.py           # Data classes
│   ├── database.py         # DynamoDB abstraction
│   ├── orchestrator.py     # Debate lifecycle
│   ├── data_service.py     # Data retrieval
│   └── api_router.py       # Request routing
│
├── ai-service/             # Multi-agent AI orchestration
│   ├── src/
│   │   ├── core/           # Debate logic
│   │   ├── handlers/       # Lambda/ECS entrypoints
│   │   └── utils/          # Utilities
│   ├── ecs_task.py         # NEW: ECS task processor
│   ├── Dockerfile.ecs      # NEW: ECS container
│   └── deps/
│       └── requirements*.txt
│
├── data_store/             # Stock data for DynamoDB
│   ├── data/               # CSV/JSON files
│   └── lambda/
│       └── data_uploader.py
│
├── cdk/                    # AWS CDK Infrastructure (TypeScript)
│   ├── src/
│   │   ├── index.ts                    # Main app (with ECS support)
│   │   ├── data-stack.ts               # DynamoDB tables
│   │   ├── compute-stack.ts            # Lambda + API Gateway
│   │   ├── ecs-stack.ts                # NEW: ECS cluster
│   │   └── frontend-stack.ts           # S3 + CloudFront (updated)
│   └── package.json
│
└── ARCHITECTURE.md         # Technical architecture details
└── QUICKSTART.md           # This file
```

## 🎯 Deployment Modes

### Standard (Lambda only)
Best for short debates (<15 minutes)
```bash
cdk deploy --all --require-approval never
```

### With ECS (Recommended)
Best for long debates and production
```bash
USE_ECS_DEBATES=true cdk deploy --all --require-approval never
```

Both Lambda and ECS can coexist during transition.

## 🔌 API Endpoints

### Health Check
```bash
GET /health
→ {"status": "healthy"}
```

### Start Debate
```bash
POST /debate
{
  "symbol": "MBB",
  "rounds": 3
}
→ {"session_id": "debate_...", "status": "submitted"}
```

### Get Status/Results
```bash
GET /debate/{session_id}
→ {"status": "completed", "verdict": {...}, ...}
```

## 🧠 Backend Services

New modular Python services for better code organization:

```python
# Initialize services
from backend.database import DynamoDBClient
from backend.orchestrator import DebateOrchestrator
from backend.data_service import DataService

db = DynamoDBClient()
orchestrator = DebateOrchestrator(db)
data_service = DataService(db)

# Use in Lambda or ECS
debate_id = orchestrator.initiate_debate("MBB", 3)
company_data = data_service.get_all_company_data("MBB")
orchestrator.complete_debate(debate_id, verdict, summary, duration)
```

**Services**:
- **models.py** - Data classes (DebateRecord, CompanyRecord, FinancialReportRecord, OhlcPriceRecord)
- **database.py** - DynamoDB abstraction with error handling and retry logic
- **orchestrator.py** - Debate lifecycle management (initiate, status, complete, fail)
- **data_service.py** - Company, financial, and price data retrieval
- **api_router.py** - Request routing and response formatting

## 📊 Costs

| Service | Cost | Notes |
|---------|------|-------|
| Lambda | $0.002/req | ~5M req/month = $10/month |
| ECS Fargate | $0.04/hr | ~100 hrs/month = $4/month |
| DynamoDB | PAY_PER_REQUEST | ~10K writes/month = $0.01 |
| CloudFront | $0.085/GB | ~100GB/month = $8.50/month |
| S3 | $0.023/GB | 1GB storage = $0.02/month |
| **Total** | | **~$22-30/month** |

## 🔐 Security

✅ No hardcoded secrets
✅ Centralized database access control
✅ IAM roles with least-privilege policies
✅ API Gateway throttling (50 req/s, 100 burst)
✅ CloudFront HTTPS only
✅ DynamoDB encryption at rest
✅ S3 bucket blocked from public access
✅ CloudWatch logging for audit trail

## 📋 Common Tasks

### Test Locally
```bash
# Frontend development server
cd frontend && npm install && npm run dev
# Opens http://localhost:5173

# Test backend services
python3 -c "from v7.backend.models import DebateRecord; print('OK')"
```

### View Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/stock-debate-advisor-compute-prod --follow

# ECS logs  
aws logs tail /ecs/stock-debate-task --follow

# API Gateway logs
aws logs tail /aws/apigateway/stock-debate-api --follow
```

### Monitor Deployment
```bash
# Watch CloudFormation progress
aws cloudformation describe-stack-events \
  --stack-name stock-debate-advisor-compute-prod \
  --query 'StackEvents[0:5]'
```

### Update Frontend
```bash
# Make changes, rebuild, and redeploy
cd frontend && npm run build
# CDK will auto-upload to S3 on next deploy
cdk deploy stock-debate-advisor-frontend-prod
```

## 🐛 Troubleshooting

**Q: Frontend shows "Cannot connect to API"**
- Check CloudFront /api/* behavior proxies to API Gateway
- Verify API Gateway endpoint is accessible: `curl $API_ENDPOINT/health`

**Q: Debates timeout at 15 minutes**
- Enable ECS: `export USE_ECS_DEBATES=true && cdk deploy --all`

**Q: Cannot import backend modules**
- Set Python path: `export PYTHONPATH=/path/to/v7`

**Q: High DynamoDB costs**
- Check TTL settings for debate results (30-day default)
- Verify no unused indexes
- Use point-in-time recovery selectively

## 📚 Documentation

- **ARCHITECTURE.md** - Technical architecture details
- **QUICKSTART.md** - This file
- See `cdk/src/` for detailed stack definitions
- See `backend/` for service documentation
- See `frontend/` for React app documentation

## 🔄 CI/CD Integration

For GitHub Actions or other CI/CD:

```bash
# Export credentials
export AWS_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# Build and deploy
cd v7/frontend && npm install && npm run build
cd ../cdk && npm install && cdk deploy --all --require-approval never
```

## ✨ Next Steps

1. **Deploy**: Follow Quick Deploy above
2. **Test**: Submit a debate from frontend
3. **Monitor**: Check CloudWatch logs
4. **Customize**: Add authentication (Cognito), real-time updates (WebSocket), etc.

---

**Version**: 7.1 | **Updated**: January 2024 | **Status**: ✅ Production Ready
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
