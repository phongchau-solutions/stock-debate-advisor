import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as path from 'path';
import { Construct } from 'constructs';

interface ComputeStackProps extends cdk.StackProps {
  companiesTable: dynamodb.Table;
  financialReportsTable: dynamodb.Table;
  ohlcPricesTable: dynamodb.Table;
  debateResultsTable: dynamodb.Table;
}

/**
 * ComputeStack: Lambda functions and API Gateway for debate orchestration
 * - Data Uploader Lambda: Automatically uploads stock data from data_store to DynamoDB on deployment
 * - Debate Lambda: Orchestrates multi-agent debate via Bedrock Claude Sonnet 3.5
 * - Health Lambda: Readiness check
 * - API Gateway: REST endpoints with CORS
 */
export class ComputeStack extends cdk.Stack {
  readonly debateApi: apigateway.RestApi;
  readonly debateLambda: lambda.Function;
  readonly dataUploaderLambda: lambda.Function;

  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    // IAM Role for Lambda: Bedrock, DynamoDB, CloudWatch
    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      description: 'Execution role for Stock Debate Lambda functions'
    });

    // Bedrock permissions (Claude Sonnet 3.5)
    lambdaRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: [
          'bedrock:InvokeModel',
          'bedrock:InvokeModelWithResponseStream'
        ],
        resources: ['arn:aws:bedrock:*::foundation-model/anthropic.claude-*'],
        effect: iam.Effect.ALLOW
      })
    );

    // DynamoDB permissions for all tables
    props.companiesTable.grantReadData(lambdaRole);
    props.financialReportsTable.grantReadData(lambdaRole);
    props.ohlcPricesTable.grantReadData(lambdaRole);
    props.debateResultsTable.grantReadWriteData(lambdaRole);
    
    // Additional write permissions for data uploader
    props.companiesTable.grantWriteData(lambdaRole);
    props.financialReportsTable.grantWriteData(lambdaRole);
    props.ohlcPricesTable.grantWriteData(lambdaRole);

    // Data Uploader Lambda - uploads data_store to DynamoDB on deployment
    this.dataUploaderLambda = new lambda.Function(this, 'DataUploaderLambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'data_uploader.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../data_store'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'cp lambda/data_uploader.py /asset-output/ && cp -r data /asset-output/'
          ]
        }
      }),
      timeout: cdk.Duration.seconds(900), // 15 minutes for data upload
      memorySize: 1024,
      ephemeralStorageSize: cdk.Size.mebibytes(2048),
      role: lambdaRole,
      environment: {
        COMPANIES_TABLE: props.companiesTable.tableName,
        FINANCIAL_REPORTS_TABLE: props.financialReportsTable.tableName,
        OHLC_PRICES_TABLE: props.ohlcPricesTable.tableName
      },
      description: 'Automatically upload stock data from data_store to DynamoDB'
    });
    cdk.Tags.of(this.dataUploaderLambda).add('Component', 'DataStore');
    cdk.Tags.of(this.dataUploaderLambda).add('Purpose', 'DataUpload');

    // Invoke data uploader Lambda after deployment to populate DynamoDB
    const dataUploaderProvider = new cdk.custom_resources.Provider(this, 'DataUploaderProvider', {
      onEventHandler: this.dataUploaderLambda,
      isCompleteHandler: new lambda.Function(this, 'DataUploaderCompleteHandler', {
        runtime: lambda.Runtime.PYTHON_3_12,
        handler: 'index.handler',
        code: lambda.Code.fromInline(`
import json
import boto3

def handler(event, context):
    return {
        'IsComplete': True,
        'Data': {
            'Status': 'DataUploadTriggered'
        }
    }
        `)
      })
    });

    // Custom resource to trigger data upload on stack deployment
    new cdk.CustomResource(this, 'DataUploadResource', {
      serviceToken: dataUploaderProvider.serviceToken,
      properties: {
        COMPANIES_TABLE: props.companiesTable.tableName,
        FINANCIAL_REPORTS_TABLE: props.financialReportsTable.tableName,
        OHLC_PRICES_TABLE: props.ohlcPricesTable.tableName
      }
    });

    // Debate Lambda function - uses Claude Sonnet 3.5 via Bedrock
    this.debateLambda = new lambda.Function(this, 'DebateLambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'src.handlers.index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../ai-service'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r deps/requirements-prod.txt -t /asset-output && cp -r src /asset-output/'
          ]
        }
      }),
      timeout: cdk.Duration.seconds(300), // 5 minutes for debate
      memorySize: 512,
      ephemeralStorageSize: cdk.Size.mebibytes(1024),
      role: lambdaRole,
      environment: {
        COMPANIES_TABLE: props.companiesTable.tableName,
        FINANCIAL_REPORTS_TABLE: props.financialReportsTable.tableName,
        OHLC_PRICES_TABLE: props.ohlcPricesTable.tableName,
        DEBATE_RESULTS_TABLE: props.debateResultsTable.tableName,
        BEDROCK_MODEL: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        AWS_LAMBDA_LOG_LEVEL: 'INFO'
      },
      description: 'Multi-agent stock debate orchestration using Bedrock Claude Sonnet 3.5'
    });
    cdk.Tags.of(this.debateLambda).add('Component', 'AI-Service');
    cdk.Tags.of(this.debateLambda).add('Purpose', 'DebateOrchestration');
    cdk.Tags.of(this.debateLambda).add('Model', 'Claude-Sonnet-3.5');

    // Health check Lambda
    const healthLambda = new lambda.Function(this, 'HealthLambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'src.handlers.index.health_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../ai-service'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r deps/requirements-health.txt -t /asset-output && cp -r src /asset-output/'
          ]
        }
      }),
      timeout: cdk.Duration.seconds(30),
      memorySize: 128,
      role: lambdaRole,
      environment: {
        COMPANIES_TABLE: props.companiesTable.tableName,
        AWS_LAMBDA_LOG_LEVEL: 'INFO'
      },
      description: 'Health check for Stock Debate API'
    });
    cdk.Tags.of(healthLambda).add('Component', 'AI-Service');
    cdk.Tags.of(healthLambda).add('Purpose', 'HealthCheck');

    // API Gateway
    this.debateApi = new apigateway.RestApi(this, 'StockDebateApi', {
      restApiName: 'Stock Debate Advisor API',
      description: 'Multi-agent stock analysis debate system with Claude Sonnet 3.5',
      deploy: true,
      deployOptions: {
        stageName: 'prod',
        throttlingBurstLimit: 100,
        throttlingRateLimit: 50,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: ['GET', 'POST', 'OPTIONS'],
        allowHeaders: ['Content-Type', 'Authorization'],
        statusCode: 200
      }
    });

    // Health endpoint: GET /health
    const healthResource = this.debateApi.root.addResource('health');
    healthResource.addMethod('GET', new apigateway.LambdaIntegration(healthLambda), {
      methodResponses: [{ statusCode: '200' }]
    });

    // Debate endpoint: POST /debate
    const debateResource = this.debateApi.root.addResource('debate');
    const debateIntegration = new apigateway.LambdaIntegration(this.debateLambda, {
      proxy: false,
      integrationResponses: [
        {
          statusCode: '200',
          responseTemplates: { 'application/json': '$input.json("$")' }
        },
        {
          statusCode: '400',
          selectionPattern: '.*"error".*',
          responseTemplates: { 'application/json': '$input.json("$")' }
        }
      ]
    });

    debateResource.addMethod('POST', debateIntegration, {
      methodResponses: [
        { statusCode: '200' },
        { statusCode: '400' },
        { statusCode: '500' }
      ]
    });

    // API Gateway outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: this.debateApi.url,
      exportName: 'StockDebateApiEndpoint',
      description: 'Stock Debate API endpoint'
    });

    new cdk.CfnOutput(this, 'HealthEndpoint', {
      value: `${this.debateApi.url}health`,
      description: 'Health check endpoint'
    });

    new cdk.CfnOutput(this, 'DebateEndpoint', {
      value: `${this.debateApi.url}debate`,
      description: 'Debate analysis endpoint'
    });

    new cdk.CfnOutput(this, 'DataUploaderLambdaArn', {
      value: this.dataUploaderLambda.functionArn,
      exportName: 'DataUploaderLambdaArn',
      description: 'Data Uploader Lambda ARN for manual invocation'
    });
  }
}
