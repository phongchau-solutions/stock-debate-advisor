#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StockDebateStack } from '../stock-debate-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
};

new StockDebateStack(app, 'StockDebateAdvisor', {
  env,
  description: 'Stock Debate Advisor - Complete Application Stack',
  tags: {
    Project: 'StockDebateAdvisor',
    Environment: process.env.ENV || 'dev',
  },
});

app.synth();
