# AWS Infrastructure Setup Guide

## Overview

This directory contains AWS CDK infrastructure for deploying the Stock Debate Advisor application to AWS. It handles:

- **VPC & Networking**: Public/private/isolated subnets across 1-3 availability zones
- **Databases**: RDS PostgreSQL 15.4 with automated backups
- **Cache**: ElastiCache Redis 7.0 cluster mode
- **Container Services**: ECS Fargate cluster with ECR repositories
- **Monitoring**: CloudWatch logs, alarms, and SSM parameter store
- **Load Balancing**: Application Load Balancer with path-based routing

## Project Structure

```
infra/
├── bin/
│   └── stock-debate-advisor.ts      # CDK app entry point
├── lib/
│   ├── stock-debate-stack.ts        # Main infrastructure stack (VPC, RDS, Redis, S3, etc.)
│   └── ecs/
│       ├── task-definitions.ts      # ECS task definitions for all services
│       └── services.ts              # ECS services with ALB and auto-scaling
├── ecs/
│   ├── task-definitions.ts
│   └── services.ts
├── scripts/
│   ├── deploy.sh                    # Main deployment script
│   └── local-setup.sh               # Local docker-compose setup
├── cdk.json                         # CDK configuration
├── tsconfig.json                    # TypeScript configuration
└── package.json                     # NPM dependencies
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Node.js 18+ and npm
- Docker Desktop
- CDK CLI: `npm install -g aws-cdk`

## Quick Start - Local Development

Run the entire stack locally using docker-compose:

```bash
# Start all services
make local-start

# View logs
make local-logs SERVICE=backend

# Stop services
make local-stop
```

Services will be available at:
- Backend: http://localhost:8000
- Data Service: http://localhost:8001
- AI Service: http://localhost:8501
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5433
- Redis: localhost:6379

## AWS Deployment

### 1. Bootstrap CDK (First Time Only)

```bash
make cdk-bootstrap
```

### 2. Deploy to Development

```bash
make deploy ENVIRONMENT=dev
```

### 3. Deploy to Production

```bash
make deploy ENVIRONMENT=prod AWS_REGION=us-west-2
```

### View Deployment Outputs

```bash
make outputs ENVIRONMENT=prod
```

## Environment Configuration

### Development Environment

- RDS: `t3.micro`, 20GB storage, 7-day backups, single AZ
- Redis: `t3.micro`, single node
- ECS: 1 task per service
- CloudWatch: 7-day retention

### Production Environment

- RDS: `t3.small`, 100GB storage, 30-day backups, Multi-AZ
- Redis: `t3.small`, 3-node cluster, automatic failover
- ECS: 2-4 tasks per service (auto-scaled)
- CloudWatch: 30-day retention

## Docker Images

All services are containerized with optimized Dockerfiles:

### Backend (Node.js)
- Base: `node:18-alpine`
- Security: Non-root user (nodejs:1001)
- Health Check: HTTP /health endpoint

### Data Service (Python)
- Base: `python:3.11-slim`
- Multi-stage build for size optimization
- Security: Non-root user (appuser:1000)
- Health Check: HTTP /health endpoint

### AI Service (Streamlit)
- Base: `python:3.11-slim`
- Multi-stage build
- Security: Non-root user (appuser:1000)
- Health Check: HTTP health check on port 8501

### Frontend (React/Vite)
- Base: `node:20-alpine`
- Multi-stage build (builder + final)
- Security: Non-root user (nextjs:1001)
- Health Check: HTTP health check

## AWS Services Used

### Compute & Orchestration
- **ECS Fargate**: Serverless container orchestration
- **ECR**: Private container registries (4 repos)
- **Application Load Balancer**: HTTP routing with health checks

### Data & Cache
- **RDS PostgreSQL**: Primary database
- **ElastiCache Redis**: Session & cache storage

### Storage
- **S3 Buckets**: Data, logs, and backup storage with encryption

### Monitoring & Logging
- **CloudWatch**: Logs, metrics, and alarms
- **SSM Parameter Store**: Configuration management
- **Secrets Manager**: Database and JWT secrets

### Networking
- **VPC**: 3-tier architecture (public/private/isolated subnets)
- **NAT Gateways**: Egress for private subnets
- **Security Groups**: Restricted ingress/egress

## Deployment Commands

### Build & Push Docker Images

```bash
# Build images locally
make build-docker

# Push to ECR
make push-ecr AWS_PROFILE=myprofile
```

### Synthesize CloudFormation

```bash
# Generate CloudFormation templates
make synth ENVIRONMENT=prod

# View what will change
make cdk-diff ENVIRONMENT=prod
```

### Deploy

```bash
# Full pipeline (build, push, deploy)
make deploy ENVIRONMENT=prod AWS_REGION=us-west-2

# Just destroy
make destroy ENVIRONMENT=prod
```

## Troubleshooting

### Check Stack Status

```bash
# List CloudFormation stacks
aws cloudformation list-stacks --region us-east-1

# View stack events
aws cloudformation describe-stack-events --stack-name StockDebateStack-prod --region us-east-1
```

### View Service Logs

```bash
# Backend logs
aws logs tail /aws/ecs/stock-debate-backend --follow

# Data service logs
aws logs tail /aws/ecs/stock-debate-data-service --follow
```

### Connect to Database

```bash
# Get RDS endpoint from outputs
ENDPOINT=$(make outputs | grep "DbEndpoint" | awk '{print $2}')

# Connect with psql
psql -h $ENDPOINT -U postgres -d stock_debate
```

### Check Container Health

```bash
# View ECS service health
aws ecs describe-services \
  --cluster stock-debate-prod \
  --services BackendService \
  --region us-east-1
```

## Cost Optimization

- **Dev**: Single AZ, t3.micro instances, minimal storage = ~$50/month
- **Prod**: Multi-AZ, t3.small instances, larger storage = ~$150/month
- Adjust instance types in `cdk.json` context values
- Set S3 lifecycle rules to move old data to Glacier

## Security Best Practices

✅ Implemented:
- All containers run as non-root users
- Secrets stored in AWS Secrets Manager
- RDS/Redis in private subnets
- VPC with restricted security groups
- ECS tasks with least-privilege IAM roles
- HTTPS-ready (configure in ALB listener)

🔧 Additional:
- Enable RDS encryption at rest
- Enable S3 versioning
- Configure WAF on ALB
- Enable VPC Flow Logs
- Set up CloudTrail logging

## Auto-Scaling Configuration

### Backend Service
- Min: 1 (dev) / 2 (prod)
- Max: 2 (dev) / 4 (prod)
- Scale on CPU > 70% or Memory > 80%

### Data Service
- Min: 1 (dev) / 2 (prod)
- Max: 2 (dev) / 4 (prod)
- Scale on CPU > 70%

### Frontend Service
- Min: 1 (dev) / 2 (prod)
- Max: 2 (dev) / 3 (prod)
- Scale on CPU > 75%

### AI Service
- Fixed at 1 task (Streamlit is stateful)

## Health Checks

All services have health checks configured:

- **Backend**: GET /health (30s interval, 30s timeout)
- **Data Service**: GET /health (30s interval, 30s timeout)
- **AI Service**: GET / (60s interval, 10s timeout)
- **Frontend**: GET / (30s interval, 5s timeout)

Failed health checks trigger automatic task replacement.

## CI/CD Integration

The infrastructure is ready for CI/CD integration:

1. GitHub Actions builds Docker images
2. Push to ECR
3. CDK deployment
4. ECS updates task definitions
5. Rolling deployment with health checks

Example GitHub Actions workflow would:
- Build & test code
- Build Docker images
- Push to ECR
- Run `cdk deploy` with approved changes

## Cleanup

```bash
# Remove local containers
make local-clean

# Destroy AWS resources
make destroy ENVIRONMENT=prod
```

⚠️ **Warning**: Destroying removes all resources including data. Ensure backups exist.

## Support

For issues:
1. Check CloudFormation events in AWS Console
2. Review ECS task logs in CloudWatch
3. Verify security group ingress/egress rules
4. Check IAM role policies
5. Review CDK context values in `cdk.json`
