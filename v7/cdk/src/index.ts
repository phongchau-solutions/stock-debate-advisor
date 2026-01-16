#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { DataStack } from './data-stack';
import { ComputeStack } from './compute-stack';
import { EcsStack } from './ecs-stack';
import { FrontendStack } from './frontend-stack';

const app = new cdk.App();

// Environment configuration
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
};

// Stack naming
const projectName = 'stock-debate-advisor';
const environment = 'prod';

// Feature flags
const useEcsForDebates = process.env.USE_ECS_DEBATES === 'true' || false;

// ============================================================================
// Data layer - DynamoDB tables
// ============================================================================
const dataStack = new DataStack(app, `${projectName}-data-${environment}`, {
  env,
  description: 'Stock Debate Advisor Data Layer (DynamoDB)',
  stackName: `${projectName}-data-${environment}`
});

// ============================================================================
// Compute layer - Lambda + API Gateway with Bedrock integration
// Short-running debates (<15 min), data upload, health checks
// ============================================================================
const computeStack = new ComputeStack(app, `${projectName}-compute-${environment}`, {
  env,
  description: 'Stock Debate Advisor Compute Layer (Lambda + API Gateway + Bedrock)',
  stackName: `${projectName}-compute-${environment}`,
  companiesTable: dataStack.companiesTable,
  financialReportsTable: dataStack.financialReportsTable,
  ohlcPricesTable: dataStack.ohlcPricesTable,
  debateResultsTable: dataStack.debateResultsTable
});

computeStack.addDependency(dataStack);

// ============================================================================
// ECS layer (Optional) - For long-running debates (>15 min)
// Set USE_ECS_DEBATES=true to enable
// ============================================================================
let ecsStack: EcsStack | undefined;
if (useEcsForDebates) {
  ecsStack = new EcsStack(app, `${projectName}-ecs-${environment}`, {
    env,
    description: 'Stock Debate Advisor ECS Layer (Fargate + SQS for long-running debates)',
    stackName: `${projectName}-ecs-${environment}`,
    companiesTable: dataStack.companiesTable,
    financialReportsTable: dataStack.financialReportsTable,
    ohlcPricesTable: dataStack.ohlcPricesTable,
    debateResultsTable: dataStack.debateResultsTable
  });
  ecsStack.addDependency(dataStack);
}

// ============================================================================
// Frontend layer - S3 + CloudFront with API endpoint
// API endpoint is injected at build time via environment variables
// ============================================================================
const frontendStack = new FrontendStack(app, `${projectName}-frontend-${environment}`, {
  env,
  description: 'Stock Debate Advisor Frontend (S3 + CloudFront)',
  stackName: `${projectName}-frontend-${environment}`,
  // Use API Gateway endpoint from compute stack
  apiEndpoint: computeStack.debateApi.url
});

// Add dependencies
frontendStack.addDependency(computeStack);
if (ecsStack) {
  frontendStack.addDependency(ecsStack);
}

// ============================================================================
// Global tags for cost tracking and organization
// ============================================================================
const tags = cdk.Tags.of(app);
tags.add('Project', projectName);
tags.add('Environment', environment);
tags.add('ManagedBy', 'CDK');
tags.add('Component', 'StockDebateAdvisor');
tags.add('CreatedDate', new Date().toISOString());

// Synthesis
app.synth();
