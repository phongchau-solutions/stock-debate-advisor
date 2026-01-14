# v7 Deployment Checklist & Getting Started

## ✅ Pre-Deployment Verification

### System Requirements
- [ ] AWS Account created (with billing enabled)
- [ ] AWS CLI v2 installed (`aws --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm 9+ installed (`npm --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] CDK CLI installed (`cdk --version`)
- [ ] Git configured (`git config --global user.name`)

### AWS Credentials
- [ ] AWS credentials configured (`aws sts get-caller-identity`)
- [ ] Default region set (`aws configure list`)
- [ ] Account ID noted: `aws sts get-caller-identity --query Account`

### Access & Permissions
- [ ] IAM user has AdministratorAccess (or equivalent)
- [ ] No service control policies blocking deployments
- [ ] No account limits on Lambda, DynamoDB, or CloudFront

## 🚀 Deployment Steps

### Phase 1: Infrastructure Setup (10 minutes)

```bash
# 1. Navigate to v7
cd /home/npc11/work/stock-debate-advisor/v7

# 2. Verify AWS credentials
aws sts get-caller-identity
# Output should show your Account ID and User ARN

# 3. Install CDK dependencies
cd cdk
npm install

# 4. Build CDK
npm run build

# 5. List stacks to verify CDK is working
cdk list

# 6. Return to v7 root
cd ..
```

**Expected Output**: List of available stacks (or "No stacks to list" on first run)

### Phase 2: Deploy Infrastructure (15-20 minutes)

```bash
# 1. Deploy the CDK stack
make deploy

# Follow the prompt to confirm deployment
# This will:
#   - Create CloudFormation stack
#   - Provision all AWS resources
#   - Output endpoint URLs
```

**Outputs to Save**:
```
✅ StockDebateFrontendURL = https://d1234.cloudfront.net
✅ StockDebateAPIEndpoint = https://api-id.execute-api.us-east-1.amazonaws.com
✅ StockDebateUserPoolId = us-east-1_xxxxx
✅ StockDebateUserPoolClientId = 1234567890abcdef
✅ StockDebateDebatesTableName = StockDebate-debates-dev
```

### Phase 3: Configure Secrets (2 minutes)

```bash
# 1. Get your Gemini API key from Google AI Studio
# https://aistudio.google.com/app/apikey

# 2. Store it in AWS Secrets Manager
aws secretsmanager create-secret \
  --name gemini-api-key \
  --secret-string '{"api_key":"YOUR_API_KEY_HERE"}'

# Verify it was stored
aws secretsmanager get-secret-value --secret-id gemini-api-key
```

### Phase 4: Deploy Frontend (5 minutes)

```bash
# 1. Build frontend
cd frontend
npm install
npm run build

# 2. Deploy to S3
make deploy-frontend

# 3. Wait for CloudFront cache to update
# This can take 2-3 minutes
```

### Phase 5: Test Application (5 minutes)

```bash
# 1. Open the CloudFront URL from Phase 2 outputs
# https://d1234.cloudfront.net

# 2. Test functionality
#   - Page loads successfully
#   - Stock symbol suggestions appear
#   - Can enter debate question
#   - Cannot submit without both fields

# 3. Create a Cognito user (or use existing)
#   - Click "Sign Up"
#   - Enter email and password
#   - Verify email

# 4. Create a debate
#   - Log in with your credentials
#   - Select stock symbol (e.g., MBB)
#   - Enter question
#   - Click "Start Debate"
#   - Wait for results (up to 15 minutes)
```

## 📊 Verification Commands

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name stock-debate-dev \
  --query 'Stacks[0].StackStatus'

# List Lambda functions
aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, "StockDebate")].FunctionName' \
  --output text

# Check DynamoDB tables
aws dynamodb list-tables \
  --query 'TableNames[?contains(@, "StockDebate")]'

# View API Gateway
aws apigateway get-rest-apis \
  --query 'items[?contains(name, "StockDebate")].[name,id]'

# Check CloudFront distribution
aws cloudfront list-distributions \
  --query 'DistributionList.Items[?Comment==`StockDebate`].[Id,Status]'
```

## 🧪 Testing the API

### Using cURL

```bash
# 1. Create a Cognito user & get token
# (Use AWS Console Cognito User Pools)

# 2. Get the user token
# This would be returned from login

# 3. Create debate
curl -X POST https://api-id.execute-api.region.amazonaws.com/debates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MBB",
    "question": "Is this a good stock?",
    "userId": "user123"
  }'

# 4. Get debate results
curl -X GET "https://api-id.execute-api.region.amazonaws.com/debates?debateId=debate-id" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Get stock data (no auth needed)
curl https://api-id.execute-api.region.amazonaws.com/data/MBB
```

### Using Postman

1. Import the API endpoint into Postman
2. Configure Cognito authorization
3. Test each endpoint
4. View response times and status codes

## 🔍 Troubleshooting

### "Stack creation failed"
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name stock-debate-dev \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'

# Common causes:
# - Invalid API key permissions
# - Service quotas exceeded
# - Resource already exists (from previous deployment)
```

### "Lambda timeout"
```bash
# Check Lambda logs
make logs

# If lambda times out:
# - Increase timeout in cdk/src/stock-debate-stack.ts
# - Reduce number of agents in ai-service/lambda/crew_agents.py
# - Redeploy with: make deploy
```

### "Cognito sign-up fails"
```bash
# Verify Cognito is configured correctly
aws cognito-idp describe-user-pool \
  --user-pool-id us-east-1_xxxxx

# Check if self-signup is enabled
# Edit CDK if needed and redeploy
```

### "Frontend shows blank page"
```bash
# Check CloudFront distribution
aws cloudfront get-distribution --id YOUR_DIST_ID

# Check S3 bucket
aws s3 ls s3://stock-debate-frontend-dev-*/

# Check browser console for errors (F12 in Chrome)
```

### "API returns 403 Unauthorized"
```bash
# Verify token in Authorization header is valid
# Check token expiration
# Regenerate token and retry

# Or test without auth (data endpoint):
curl https://api-id.execute-api.region.amazonaws.com/data/MBB
```

## 📈 Monitoring

### View Live Logs
```bash
# Tail Lambda logs in real-time
make logs

# Or manually
aws logs tail /aws/lambda/StockDebate-debate-orchestrator-dev --follow
```

### Monitor Performance
```bash
# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=StockDebate-debate-orchestrator-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedWriteCapacityUnits \
  --dimensions Name=TableName,Value=StockDebate-debates-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

### Health Check
```bash
# Run automated health check
./scripts/health-check.sh dev
```

## 🧹 Cleanup

### Delete Everything (DESTRUCTIVE!)
```bash
# WARNING: This cannot be undone!
make destroy

# Or manually:
aws cloudformation delete-stack --stack-name stock-debate-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name stock-debate-dev
```

### Clean Local Files
```bash
make clean
```

## 📝 Next Steps After Deployment

1. **Customize Agents**
   - Edit `ai-service/lambda/crew_agents.py`
   - Add more analysis perspectives
   - Redeploy: `make deploy`

2. **Add Data Sources**
   - Update `data_store/lambda/index.py`
   - Integrate yfinance, Alpha Vantage, etc.
   - Redeploy: `make deploy`

3. **Enhance Frontend**
   - Add charts with Chart.js
   - Real-time updates with WebSockets
   - User history & saved debates
   - Redeploy: `make deploy-frontend`

4. **Set Up Monitoring**
   - Create CloudWatch alarms
   - SNS notifications for errors
   - Dashboard for key metrics

5. **Implement CI/CD**
   - GitHub Actions for auto-deploy
   - Test on PR creation
   - Deploy on merge to main

6. **Scale to Production**
   - Use `environment=prod` in Makefile
   - Enable point-in-time recovery (DynamoDB)
   - Set up regular backups
   - Use custom domain in CloudFront

## 💡 Tips & Best Practices

### Development
```bash
# Keep costs low during development
# - Use on-demand DynamoDB (automatic scaling)
# - Delete unused stacks regularly
# - Monitor Lambda invocations
# - Use same AWS account for development

# Test locally before deploying
cd frontend
npm run dev
# Open http://localhost:5173
```

### Monitoring
```bash
# Set up CloudWatch alarms for production
# - Lambda errors > 5 in 5 minutes
# - Lambda duration > 10 seconds
# - API 5xx errors
# - DynamoDB throttled requests
```

### Cost Optimization
```bash
# Reduce costs by:
# - Setting DynamoDB TTL for old data
# - Using CloudFront caching
# - Reducing Lambda memory (if slow)
# - Using Lambda layers (reduces package size)
# - Cleaning up unused resources
```

## 🎯 Success Criteria

After deployment, verify:
- [ ] CloudFront URL is accessible
- [ ] Frontend loads without errors
- [ ] Can create Cognito user account
- [ ] Can authenticate & log in
- [ ] Can create debate successfully
- [ ] Debate results are returned
- [ ] Results are stored in DynamoDB
- [ ] Stock data is cached properly
- [ ] No Lambda errors in CloudWatch
- [ ] Health check script shows all green

---

**Total Deployment Time**: ~45-60 minutes (including configuration)
**Status**: Ready for deployment
**Support**: See README.md for detailed troubleshooting
