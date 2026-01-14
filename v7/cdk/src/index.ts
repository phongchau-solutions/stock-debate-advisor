#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { DataStack } from './data-stack';
import { ComputeStack } from './compute-stack';
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

// Data layer - DynamoDB tables
const dataStack = new DataStack(app, `${projectName}-data-${environment}`, {
  env,
  description: 'Stock Debate Advisor Data Layer (DynamoDB)',
  stackName: `${projectName}-data-${environment}`
});

// Compute layer - Lambda + API Gateway with Bedrock integration
const computeStack = new ComputeStack(app, `${projectName}-compute-${environment}`, {
  env,
  description: 'Stock Debate Advisor Compute Layer (Lambda + API Gateway + Bedrock)',
  stackName: `${projectName}-compute-${environment}`,
  companiesTable: dataStack.companiesTable,
  financialReportsTable: dataStack.financialReportsTable,
  ohlcPricesTable: dataStack.ohlcPricesTable,
  debateResultsTable: dataStack.debateResultsTable
});

// Add dependency: compute depends on data
computeStack.addDependency(dataStack);

// Frontend layer - S3 + CloudFront
const frontendStack = new FrontendStack(app, `${projectName}-frontend-${environment}`, {
  env,
  description: 'Stock Debate Advisor Frontend (S3 + CloudFront)',
  stackName: `${projectName}-frontend-${environment}`,
  apiEndpoint: computeStack.debateApi.url
});

// Add dependency: frontend depends on compute (needs API endpoint)
frontendStack.addDependency(computeStack);

// Root stack tags
const tags = cdk.Tags.of(app);
tags.add('Project', projectName);
tags.add('Environment', environment);
tags.add('ManagedBy', 'CDK');
tags.add('CreatedDate', new Date().toISOString());

// Synthesis
app.synth();
