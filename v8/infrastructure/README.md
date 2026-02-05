# Infrastructure

Infrastructure as Code (IaC) and deployment configurations.

## Contents

### terraform/
Terraform configurations for cloud resources.

### docker/
Docker Compose files for local development.

## Docker Development

```bash
# Start all services
docker-compose -f docker/docker-compose.dev.yml up

# Start specific service
docker-compose -f docker/docker-compose.dev.yml up debate-service

# Stop all services
docker-compose -f docker/docker-compose.dev.yml down
```

## Terraform

```bash
# Initialize Terraform
cd terraform/environments/dev
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply
```

## Status

🚧 **In Development** - Structure created, implementation pending
