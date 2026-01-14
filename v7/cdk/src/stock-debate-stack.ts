import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';
import { Construct } from 'constructs';

export class StockDebateStack extends cdk.Stack {
  public apiEndpoint: string;
  public frontendUrl: string;
  public cognitoUserPoolId: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const environment = this.node.tryGetContext('environment') || 'dev';
    const stackPrefix = this.node.tryGetContext('stackPrefix') || 'StockDebate';

    // ========== COGNITO USER POOL ==========
    const userPool = new cognito.UserPool(this, `${stackPrefix}UserPool`, {
      userPoolName: `${stackPrefix}-${environment}`,
      selfSignUpEnabled: true,
      // autoVerifiedAttributes removed - use signInAliases instead
      signInAliases: {
        email: true
      },
      standardAttributes: {
        email: {
          required: true,
          mutable: false,
        },
        fullname: {
          mutable: true,
        },
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
    });

    const userPoolClient = userPool.addClient(`${stackPrefix}Client`, {
      userPoolClientName: `${stackPrefix}-client-${environment}`,
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      oAuth: {
        flows: {
          implicitCodeGrant: true,
          authorizationCodeGrant: true,
        },
        scopes: [cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL, cognito.OAuthScope.PROFILE],
        callbackUrls: [
          environment === 'prod' 
            ? 'https://yourdomain.com/callback' 
            : 'http://localhost:5173/callback',
        ],
        logoutUrls: [
          environment === 'prod'
            ? 'https://yourdomain.com/logout'
            : 'http://localhost:5173/logout',
        ],
      },
    });

    // ========== S3 BUCKET FOR FRONTEND ==========
    const frontendBucket = new s3.Bucket(this, `${stackPrefix}FrontendBucket`, {
      bucketName: `${stackPrefix.toLowerCase()}-frontend-${environment}-${cdk.Stack.of(this).account}`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: false,
    });

    // ========== CLOUDFRONT DISTRIBUTION ==========
    const cloudFrontOAI = new cloudfront.OriginAccessIdentity(this, 'CloudFrontOAI');

    frontendBucket.grantRead(cloudFrontOAI);

    const distribution = new cloudfront.Distribution(this, `${stackPrefix}Distribution`, {
      defaultBehavior: {
        origin: new origins.S3Origin(frontendBucket, {
          originAccessIdentity: cloudFrontOAI,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
      enabled: true,
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
    });

    // ========== DYNAMODB TABLES ==========
    // Debates table
    const debatesTable = new dynamodb.Table(this, `${stackPrefix}DebatesTable`, {
      tableName: `${stackPrefix}-debates-${environment}`,
      partitionKey: { name: 'debateId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: environment === 'prod',
    });

    debatesTable.addGlobalSecondaryIndex({
      indexName: 'userIdIndex',
      partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Stock symbols cache table
    const stockCacheTable = new dynamodb.Table(this, `${stackPrefix}StockCacheTable`, {
      tableName: `${stackPrefix}-stock-cache-${environment}`,
      partitionKey: { name: 'symbol', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      timeToLiveAttribute: 'ttl',
    });

    // ========== LAMBDA LAYER FOR SHARED DEPENDENCIES ==========
    const lambdaLayer = new lambda.LayerVersion(this, `${stackPrefix}SharedLayer`, {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda-layer')),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      layerVersionName: `${stackPrefix}-shared-${environment}`,
    });

    // ========== LAMBDA FUNCTIONS ==========

    // Debate Orchestrator Lambda
    const debateOrchestratorLambda = new lambda.Function(this, `${stackPrefix}DebateOrchestrator`, {
      functionName: `${stackPrefix}-debate-orchestrator-${environment}`,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'src.handlers.index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../ai-service')),
      environment: {
        DEBATES_TABLE: debatesTable.tableName,
        STOCK_CACHE_TABLE: stockCacheTable.tableName,
        GEMINI_API_KEY: cdk.SecretValue.secretsManager('gemini-api-key', {
          jsonField: 'api_key',
        }).toString(),
        ENVIRONMENT: environment,
      },
      timeout: cdk.Duration.seconds(900), // 15 minutes for long-running debates
      memorySize: 1024,
      layers: [lambdaLayer],
    });

    debatesTable.grantReadWriteData(debateOrchestratorLambda);
    stockCacheTable.grantReadWriteData(debateOrchestratorLambda);

    // Data Loader Lambda
    const dataLoaderLambda = new lambda.Function(this, `${stackPrefix}DataLoader`, {
      functionName: `${stackPrefix}-data-loader-${environment}`,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../data_store/lambda')),
      environment: {
        STOCK_CACHE_TABLE: stockCacheTable.tableName,
        CACHE_TTL: '86400', // 24 hours
        ENVIRONMENT: environment,
      },
      timeout: cdk.Duration.seconds(60),
      memorySize: 512,
      layers: [lambdaLayer],
    });

    stockCacheTable.grantReadWriteData(dataLoaderLambda);

    // ========== API GATEWAY ==========
    const api = new apigateway.RestApi(this, `${stackPrefix}API`, {
      restApiName: `${stackPrefix}-api-${environment}`,
      description: 'Stock Debate Advisor API',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'Authorization'],
      },
    });

    // Cognito authorizer
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, `${stackPrefix}Authorizer`, {
      cognitoUserPools: [userPool],
    });

    // Debates resource
    const debatesResource = api.root.addResource('debates');

    debatesResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(debateOrchestratorLambda),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    debatesResource.addMethod(
      'GET',
      new apigateway.LambdaIntegration(debateOrchestratorLambda),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Data resource
    const dataResource = api.root.addResource('data');
    dataResource.addResource('{symbol}').addMethod(
      'GET',
      new apigateway.LambdaIntegration(dataLoaderLambda)
    );

    // ========== OUTPUTS ==========
    this.apiEndpoint = api.url;
    this.frontendUrl = distribution.domainName;
    this.cognitoUserPoolId = userPool.userPoolId;

    new cdk.CfnOutput(this, `${stackPrefix}APIEndpoint`, {
      value: api.url,
      description: 'API Gateway endpoint',
      exportName: `${stackPrefix}-api-endpoint-${environment}`,
    });

    new cdk.CfnOutput(this, `${stackPrefix}FrontendURL`, {
      value: `https://${distribution.domainName}`,
      description: 'CloudFront distribution URL',
      exportName: `${stackPrefix}-frontend-url-${environment}`,
    });

    new cdk.CfnOutput(this, `${stackPrefix}UserPoolId`, {
      value: userPool.userPoolId,
      description: 'Cognito User Pool ID',
      exportName: `${stackPrefix}-user-pool-id-${environment}`,
    });

    new cdk.CfnOutput(this, `${stackPrefix}UserPoolClientId`, {
      value: userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
      exportName: `${stackPrefix}-client-id-${environment}`,
    });

    new cdk.CfnOutput(this, `${stackPrefix}DebatesTableName`, {
      value: debatesTable.tableName,
      description: 'DynamoDB Debates Table',
      exportName: `${stackPrefix}-debates-table-${environment}`,
    });
  }
}
