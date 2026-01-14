# AWS Deployment - AI Service

**Note**: AWS infrastructure is managed via AWS CDK in the `infra/` directory. This guide provides reference information for manual deployments and testing.

## CDK-Based Deployment (Recommended)

AWS infrastructure for the Stock Debate Advisor is defined and deployed using **AWS Cloud Development Kit (CDK)**.

### Quick Deploy via CDK

```bash
# Navigate to infrastructure directory
cd ../infra

# Install dependencies
npm install

# Deploy to AWS
cdk deploy

# View deployed resources
cdk ls
```

For detailed CDK setup and deployment instructions, see [infra/README.md](../infra/README.md)

## Infrastructure Components (Deployed via CDK)

The CDK stack automatically provisions:

- **ECS Fargate Cluster** - Managed container orchestration
- **Application Load Balancer** - Traffic distribution
- **API Gateway** - REST API endpoint
- **RDS PostgreSQL** - Managed database
- **CloudWatch** - Logging and monitoring
- **Secrets Manager** - Secure credential management
- **VPC & Security Groups** - Network isolation
- **IAM Roles** - Proper access control

## Environment Configuration

### Required Secrets (stored in AWS Secrets Manager)

```bash
# These are set during CDK deployment
stock-debate/gemini-api-key       # Google Gemini API key
stock-debate/database-password    # PostgreSQL password
stock-debate/api-key              # API authentication key (optional)
```

### Environment Variables

```env
# Set these in ECS task definition or Lambda environment
GEMINI_API_KEY=<from-secrets-manager>
CREWAI_MODEL=gemini-2.5-pro
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/stock_debate
DATA_SERVICE_URL=http://data-service-alb/api/v1
LOG_LEVEL=INFO
CREW_VERBOSE=True
CREW_MEMORY=True
```

## Docker Image Deployment

### Build and Push to ECR

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t stock-debate-ai-service:latest .

# Tag for ECR
docker tag stock-debate-ai-service:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/stock-debate-ai-service:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/stock-debate-ai-service:latest
```

### ECS Task Definition

The CDK stack creates the ECS task definition with:
- Proper resource allocation (1024 CPU, 2048 MB memory)
- CloudWatch log groups
- IAM role for accessing secrets and resources
- Health checks

To update the task definition:

```bash
cd ../infra
# Modify lib/ecs-stack.ts
cdk deploy --require-approval never
```

## Deployment Strategies

### Blue-Green Deployment

```bash
# The CDK stack supports blue-green deployment via CodeDeploy
# Create a new task definition version
# ECS will gradually shift traffic from old to new version
```

### Canary Deployment

```bash
# Deploy to a percentage of tasks first
# Monitor metrics before full rollout
# Configured in infra/lib/ecs-stack.ts
```

## Monitoring & Logging

### CloudWatch Logs

```bash
# View logs for AI Service
aws logs tail /ecs/stock-debate-ai-service --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/stock-debate-ai-service \
  --filter-pattern "ERROR"

# Create metric filters
aws logs put-metric-filter \
  --log-group-name /ecs/stock-debate-ai-service \
  --filter-name ErrorCount \
  --filter-pattern "[ERROR]"
```

### CloudWatch Metrics

```bash
# View custom metrics
aws cloudwatch get-metric-statistics \
  --namespace "StockDebateAdvisor/AI" \
  --metric-name DebateCompletionTime \
  --start-time 2026-01-14T00:00:00Z \
  --end-time 2026-01-15T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum
```

### CloudWatch Alarms

```bash
# Set up alarms for critical metrics
aws cloudwatch put-metric-alarm \
  --alarm-name stock-debate-ai-error-rate \
  --alarm-description "Alert if error rate > 5%" \
  --metric-name ErrorRate \
  --namespace StockDebateAdvisor/AI \
  --statistic Average \
  --period 60 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

## Manual Testing (Local/Development)

### Local Docker Testing

```bash
# Build image locally
docker build -t stock-debate-ai-service:test .

# Run with test configuration
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-test-key \
  -e CREWAI_MODEL=gemini-2.5-pro \
  stock-debate-ai-service:test
```

### Integration Testing

```bash
# Test against deployed API Gateway
export API_ENDPOINT="https://api.example.com"

python test_api.py

# or manually
curl -X GET https://api.example.com/health
curl -X POST https://api.example.com/api/v1/debate/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "MBB.VN", "rounds": 20}'
```

## Rollback Procedure

### Rollback to Previous ECS Task Definition

```bash
# List previous task definitions
aws ecs list-task-definitions --sort DESC --max-items 10

# Update service to use previous task definition
aws ecs update-service \
  --cluster stock-debate-production \
  --service stock-debate-ai-service \
  --task-definition stock-debate-ai-service:99 \
  --force-new-deployment
```

### Rollback via CDK

```bash
cd ../infra

# Revert to previous git commit
git checkout <previous-commit>

# Redeploy
cdk deploy --require-approval never
```

## Cost Optimization

### ECS Fargate Pricing

- **CPU**: $0.04048 per vCPU-hour
- **Memory**: $0.004445 per GB-hour

Current allocation: 1 vCPU, 2GB = ~$60/month (on-demand)

### Cost Reduction Options

1. **Reserved Capacity**: 30-70% discount with commitments
2. **Spot Instances**: 70% discount (but interruptible)
3. **Auto-scaling**: Scale down during off-peak hours
4. **Right-sizing**: Reduce CPU/memory if underutilized

### Set Auto-Scaling Policy

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/stock-debate-production/stock-debate-ai-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

# Create scaling policy (scale up when CPU > 70%)
aws application-autoscaling put-scaling-policy \
  --policy-name scale-up \
  --service-namespace ecs \
  --resource-id service/stock-debate-production/stock-debate-ai-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    TargetValue=70,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}
```

## Troubleshooting

### Service Won't Start

```bash
# Check ECS task logs
aws ecs describe-tasks \
  --cluster stock-debate-production \
  --tasks $(aws ecs list-tasks --cluster stock-debate-production --query 'taskArns[0]' --output text) \
  --query 'tasks[0].{LastStatus:lastStatus,StoppedReason:stoppedReason}'

# View container logs
aws logs tail /ecs/stock-debate-ai-service --follow
```

### Health Check Failing

```bash
# Check security groups
aws ec2 describe-security-groups --filters Name=group-name,Values=stock-debate-ai-sg

# Test endpoint accessibility
curl http://ECS_PRIVATE_IP:8000/health

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...
```

### Database Connection Issues

```bash
# Check RDS instance status
aws rds describe-db-instances \
  --db-instance-identifier stock-debate-db

# Test connectivity from ECS task
aws ecs execute-command \
  --cluster stock-debate-production \
  --task <task-id> \
  --container stock-debate-ai-service \
  --command "/bin/bash" \
  --interactive
```

## References

- [CDK Infrastructure Guide](../infra/README.md)
- [ECS Task Definition](./ecs-task-definition.json)
- [Setup Guide](./SETUP_GUIDE.md)
- [API Integration Guide](./API_INTEGRATION.md)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)

