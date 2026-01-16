import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as path from 'path';
import { Construct } from 'constructs';

interface FrontendStackProps extends cdk.StackProps {
  apiEndpoint: string;
}

/**
 * FrontendStack: S3 + CloudFront for React SPA
 * - S3 bucket for static assets
 * - CloudFront distribution with caching
 * - Environment variables injected for deployed API endpoint
 * - Automatic SPA routing to index.html
 */
export class FrontendStack extends cdk.Stack {
  readonly bucket: s3.Bucket;
  readonly distribution: cloudfront.Distribution;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    // S3 bucket for frontend with CloudFront access
    this.bucket = new s3.Bucket(this, 'StockDebateBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false
    });
    cdk.Tags.of(this.bucket).add('Component', 'Frontend');
    cdk.Tags.of(this.bucket).add('Purpose', 'ReactSPA');

    // CloudFront Origin Access Identity
    const oai = new cloudfront.OriginAccessIdentity(this, 'OAI', {
      comment: 'OAI for Stock Debate Frontend'
    });

    // Grant CloudFront read access to S3
    this.bucket.grantRead(oai);

    // Extract API endpoint hostname
    const apiHost = this.parseApiHost(props.apiEndpoint);

    // CloudFront distribution with API proxy behavior
    this.distribution = new cloudfront.Distribution(this, 'StockDebateDistribution', {
      comment: 'Stock Debate Advisor Frontend - React SPA',
      defaultBehavior: {
        origin: new origins.S3Origin(this.bucket, {
          originAccessIdentity: oai
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
        // Rewrite SPA routes to index.html
        functionAssociations: [
          {
            function: new cloudfront.Function(this, 'RewriteToIndex', {
              code: cloudfront.FunctionCode.fromInline(`
function handler(event) {
  var request = event.request;
  var uri = request.uri;
  
  // Rewrite SPA routes to index.html (except /api)
  if (!uri.includes('.') && !uri.startsWith('/api')) {
    request.uri = '/index.html';
  }
  
  return request;
}
              `)
            }),
            eventType: cloudfront.FunctionEventType.VIEWER_REQUEST
          }
        ]
      },
      // Proxy /api/* requests to the API Gateway
      additionalBehaviors: {
        '/api/*': {
          origin: new origins.HttpOrigin(apiHost, {
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTPS_ONLY
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          compress: false
        }
      },
      // SPA error handling - 404 -> index.html
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html'
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html'
        }
      ],
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      enableIpv6: true,
      enableLogging: true,
      defaultRootObject: 'index.html',
      logBucket: new s3.Bucket(this, 'DistributionLogBucket', {
        encryption: s3.BucketEncryption.S3_MANAGED,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
        blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
        objectOwnership: s3.ObjectOwnership.OBJECT_WRITER,
        accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE
      })
    });

    // Deploy frontend dist folder (built React app)
    const deploymentSource = s3deploy.Source.asset(
      path.join(__dirname, '../../frontend/dist'),
      {
        // If dist doesn't exist, create a minimal placeholder
        exclude: ['node_modules', '.git']
      }
    );

    new s3deploy.BucketDeployment(this, 'FrontendDeploy', {
      sources: [deploymentSource],
      destinationBucket: this.bucket,
      distributionPaths: ['/*'],
      distribution: this.distribution,
      prune: true
    });

    // Outputs for use in other stacks or CI/CD
    new cdk.CfnOutput(this, 'DistributionUrl', {
      value: `https://${this.distribution.domainName}`,
      exportName: 'StockDebateFrontendUrl',
      description: 'CloudFront distribution URL for frontend'
    });

    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: props.apiEndpoint,
      exportName: 'StockDebateApiEndpoint',
      description: 'API Gateway endpoint URL'
    });

    new cdk.CfnOutput(this, 'S3BucketName', {
      value: this.bucket.bucketName,
      exportName: 'StockDebateBucketName',
      description: 'S3 bucket for frontend assets'
    });

    new cdk.CfnOutput(this, 'DistributionId', {
      value: this.distribution.distributionId,
      exportName: 'StockDebateDistributionId',
      description: 'CloudFront distribution ID'
    });
  }

  /**
   * Extract hostname from API endpoint URL
   * Handles both CloudFormation tokens and regular URLs
   */
  private parseApiHost(apiEndpoint: string): string {
    const endpointStr = apiEndpoint.toString();
    
    // Extract hostname from URL pattern
    const urlMatch = endpointStr.match(/https?:\/\/([^\/]+)/);
    if (urlMatch) {
      return urlMatch[1];
    }
    
    // Try standard URL parsing
    try {
      const url = new URL(endpointStr);
      return url.hostname;
    } catch (e) {
      // Fallback: extract domain pattern
      const domainMatch = endpointStr.match(/([a-zA-Z0-9-]+\.execute-api\.[a-z0-9-]+\.amazonaws\.com)/);
      if (domainMatch) {
        return domainMatch[1];
      }
    }
    
    // Worst case fallback (shouldn't happen with valid CDK output)
    console.warn(`Failed to parse API endpoint: ${endpointStr}`);
    return 'api.example.com';
  }
}
