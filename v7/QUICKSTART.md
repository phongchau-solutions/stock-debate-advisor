# Quick Start Guide - v7

## 5-Minute Setup

### 1. Prerequisites
```bash
# Check versions
aws --version        # AWS CLI v2+
node --version       # Node 18+
npm --version        # npm 9+
python3 --version    # Python 3.12+
```

### 2. Configure AWS
```bash
aws configure
# Enter: Access Key ID, Secret Key, Region (us-east-1), Output (json)
```

### 3. Deploy Infrastructure
```bash
cd v7
make install
make deploy
```

### 4. Get Outputs
```bash
# The deploy command shows all outputs
# Save these URLs:
# - API Endpoint
# - Frontend URL
# - User Pool ID
```

### 5. Set API Key
```bash
aws secretsmanager create-secret \
  --name gemini-api-key \
  --secret-string '{"api_key":"your-gemini-api-key"}'
```

### 6. Deploy Frontend
```bash
make deploy-frontend
```

### 7. Access App
Open the CloudFront URL in your browser:
```
https://<cloudfront-id>.cloudfront.net
```

## Common Tasks

### Test Locally
```bash
# Frontend
cd frontend
npm install
npm run dev
# Open http://localhost:5173

# AI Service
cd ai-service
pip install -r lambda/requirements.txt
python -m pytest test/
```

### View Logs
```bash
make logs
# or
aws logs tail /aws/lambda/StockDebate-debate-orchestrator-dev --follow
```

### Make Changes
```bash
# CDK changes
cd cdk
# Edit stack
npm run build
npm run cdk:diff      # See what changed
npm run cdk:deploy    # Deploy

# Frontend changes
cd frontend
npm run build
make deploy-frontend
```

### Destroy Everything
```bash
make destroy
# WARNING: This cannot be undone!
```

## Troubleshooting

### "API key not found"
→ Store secret: `aws secretsmanager create-secret --name gemini-api-key --secret-string '{"api_key":"..."}'`

### "Access Denied" in Lambda
→ Check IAM role has permissions for DynamoDB and Secrets Manager

### Frontend shows blank page
→ Check CloudFront logs: `aws cloudfront get-distribution --id <dist-id>`

### Lambda timeout
→ Increase timeout in `cdk/src/stock-debate-stack.ts` (max 15 minutes)

## Next Steps

1. **Add real data sources**: Update `data_store/lambda/index.py`
2. **Customize agents**: Modify `ai-service/lambda/crew_agents.py`
3. **Style frontend**: Edit `frontend/src/index.css`
4. **Set up CI/CD**: Create GitHub Actions workflow
5. **Monitor**: Enable CloudWatch alarms

## Documentation

- Full docs: [README.md](README.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- AI Service: [ai-service/README.md](ai-service/README.md)
- Data Store: [data_store/README.md](data_store/README.md)
