#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { StockDebateStack } from './stock-debate-stack';

const app = new cdk.App();

const environment = app.node.tryGetContext('environment') || 'dev';
const region = process.env.AWS_REGION || 'us-east-1';
const account = process.env.AWS_ACCOUNT_ID || '123456789012';

new StockDebateStack(app, `StockDebate-${environment}`, {
  env: {
    account,
    region,
  },
  description: `Stock Debate Advisor Stack - ${environment}`,
  stackName: `stock-debate-${environment}`,
});

app.synth();
