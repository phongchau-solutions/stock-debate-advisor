.PHONY: help install lint build-docker push-ecr deploy destroy synth outputs \
        local-start local-stop local-restart local-logs local-status local-clean \
        cdk-diff cdk-bootstrap test

ENVIRONMENT ?= dev
AWS_REGION ?= us-east-1
AWS_PROFILE ?= default

help:
	@echo "Stock Debate Advisor - Makefile Commands"
	@echo ""
	@echo "Infrastructure Commands:"
	@echo "  make install           Install CDK dependencies"
	@echo "  make lint              Lint CDK infrastructure"
	@echo "  make build-docker      Build Docker images locally"
	@echo "  make push-ecr          Push images to AWS ECR"
	@echo "  make synth             Synthesize CDK (generate CloudFormation)"
	@echo "  make cdk-diff          Show CDK diff before deployment"
	@echo "  make cdk-bootstrap     Bootstrap CDK environment"
	@echo "  make deploy            Full deployment pipeline"
	@echo "  make destroy           Destroy AWS stack"
	@echo "  make outputs           Show stack outputs"
	@echo ""
	@echo "Local Development Commands:"
	@echo "  make local-start       Start all services locally"
	@echo "  make local-stop        Stop all services"
	@echo "  make local-restart     Restart all services"
	@echo "  make local-logs        Show service logs"
	@echo "  make local-status      Show service status"
	@echo "  make local-clean       Remove containers and volumes"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test              Run test suite"
	@echo ""
	@echo "Variables:"
	@echo "  ENVIRONMENT=dev/prod   (default: dev)"
	@echo "  AWS_REGION=...         (default: us-east-1)"
	@echo "  AWS_PROFILE=...        (default: default)"
	@echo ""
	@echo "Examples:"
	@echo "  make deploy ENVIRONMENT=prod AWS_REGION=us-west-2"
	@echo "  make local-logs SERVICE=backend"

install:
	@echo "Installing dependencies..."
	cd infra && npm install

lint:
	@echo "Linting CDK infrastructure..."
	cd infra && npm run lint || echo "Linting completed with warnings"

build-docker:
	@echo "Building Docker images..."
	bash infra/scripts/deploy.sh build-docker

push-ecr:
	@echo "Pushing images to ECR..."
	AWS_PROFILE=$(AWS_PROFILE) AWS_REGION=$(AWS_REGION) bash infra/scripts/deploy.sh push-ecr

synth:
	@echo "Synthesizing CDK stack..."
	cd infra && cdk synth --profile $(AWS_PROFILE) --context environment=$(ENVIRONMENT)

cdk-diff:
	@echo "Showing CDK diff..."
	cd infra && cdk diff --profile $(AWS_PROFILE) --context environment=$(ENVIRONMENT)

cdk-bootstrap:
	@echo "Bootstrapping CDK environment..."
	cd infra && cdk bootstrap aws://$(shell aws sts get-caller-identity --query Account --output text --profile $(AWS_PROFILE))/$(AWS_REGION) --profile $(AWS_PROFILE)

deploy: install lint build-docker push-ecr
	@echo "Deploying to AWS..."
	ENVIRONMENT=$(ENVIRONMENT) AWS_REGION=$(AWS_REGION) AWS_PROFILE=$(AWS_PROFILE) bash infra/scripts/deploy.sh deploy

destroy:
	@echo "Destroying AWS stack..."
	ENVIRONMENT=$(ENVIRONMENT) AWS_REGION=$(AWS_REGION) AWS_PROFILE=$(AWS_PROFILE) bash infra/scripts/deploy.sh destroy

outputs:
	@echo "Fetching stack outputs..."
	ENVIRONMENT=$(ENVIRONMENT) AWS_REGION=$(AWS_REGION) AWS_PROFILE=$(AWS_PROFILE) bash infra/scripts/deploy.sh outputs

local-start:
	@echo "Starting local services..."
	bash infra/scripts/local-setup.sh start

local-stop:
	@echo "Stopping local services..."
	bash infra/scripts/local-setup.sh stop

local-restart:
	@echo "Restarting local services..."
	bash infra/scripts/local-setup.sh restart

local-logs:
	@bash infra/scripts/local-setup.sh logs $(SERVICE)

local-status:
	@bash infra/scripts/local-setup.sh status

local-clean:
	@echo "Cleaning local environment..."
	bash infra/scripts/local-setup.sh clean

test:
	@echo "Running test suite..."
	@if [ -f "package.json" ]; then npm test; else echo "No tests found"; fi

.DEFAULT_GOAL := help
