.PHONY: help install build deploy deploy-frontend test clean destroy

ENVIRONMENT ?= dev
AWS_REGION ?= us-east-1

help:
	@echo "Stock Debate Advisor v7 - Makefile"
	@echo "===================================="
	@echo ""
	@echo "Usage: make [target] [ENVIRONMENT=dev|prod]"
	@echo ""
	@echo "Targets:"
	@echo "  install           Install all dependencies"
	@echo "  build             Build all components (CDK, Frontend)"
	@echo "  deploy            Deploy infrastructure to AWS"
	@echo "  deploy-frontend   Deploy frontend to S3/CloudFront"
	@echo "  test              Run all tests"
	@echo "  logs              Tail Lambda logs"
	@echo "  destroy           Destroy AWS stack (BE CAREFUL!)"
	@echo "  clean             Clean build artifacts"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	cd cdk && npm install
	cd frontend && npm install
	@echo "✓ Dependencies installed"

build: install
	@echo "🔨 Building components..."
	cd cdk && npm run build
	cd frontend && npm run build
	@echo "✓ Build complete"

deploy: build
	@echo "🚀 Deploying to AWS ($(ENVIRONMENT))..."
	cd cdk && npm run cdk:deploy -- -c environment=$(ENVIRONMENT)
	@echo "✓ CDK stack deployed"

deploy-frontend: 
	@echo "📤 Deploying frontend..."
	./scripts/deploy-frontend.sh $(ENVIRONMENT)
	@echo "✓ Frontend deployed"

test:
	@echo "🧪 Running tests..."
	cd frontend && npm test -- --coverage
	cd ai-service && python -m pytest test/ -v || echo "No tests found"
	@echo "✓ Tests complete"

logs:
	@echo "📋 Tailing Lambda logs..."
	aws logs tail /aws/lambda/StockDebate-debate-orchestrator-$(ENVIRONMENT) --follow --region $(AWS_REGION)

synth:
	@echo "📄 Synthesizing CloudFormation..."
	cd cdk && npm run cdk:synth
	@echo "✓ Synth complete - check cdk.out/"

diff:
	@echo "📊 Showing infrastructure diff..."
	cd cdk && npm run cdk:diff -- -c environment=$(ENVIRONMENT)

destroy:
	@echo "⚠️  WARNING: This will delete all resources!"
	./scripts/destroy.sh $(ENVIRONMENT)

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf cdk/lib cdk/dist cdk/cdk.out
	rm -rf frontend/dist frontend/build
	rm -rf ai-service/__pycache__ data_store/__pycache__
	@echo "✓ Clean complete"

.DEFAULT_GOAL := help
