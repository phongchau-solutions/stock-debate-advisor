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
 * - API client configuration for Bedrock-backed AI service
 */
export class FrontendStack extends cdk.Stack {
  readonly bucket: s3.Bucket;
  readonly distribution: cloudfront.Distribution;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    // S3 bucket for frontend
    this.bucket = new s3.Bucket(this, 'StockDebateBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false
    });
    cdk.Tags.of(this.bucket).add('Component', 'Frontend');
    cdk.Tags.of(this.bucket).add('Purpose', 'SPA');

    // CloudFront Origin Access Identity
    const oai = new cloudfront.OriginAccessIdentity(this, 'OAI', {
      comment: 'OAI for Stock Debate Frontend'
    });

    // Grant CloudFront read access to S3
    this.bucket.grantRead(oai);

    // CloudFront distribution
    this.distribution = new cloudfront.Distribution(this, 'StockDebateDistribution', {
      comment: 'Stock Debate Advisor Frontend',
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessIdentity(this.bucket, { originAccessIdentity: oai }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
        functionAssociations: [
          {
            function: new cloudfront.Function(this, 'RewriteToIndex', {
              code: cloudfront.FunctionCode.fromInline(
                `function handler(event) {
                  var request = event.request;
                  var uri = request.uri;
                  
                  // Rewrite SPA routes to index.html for React Router
                  if (!uri.includes('.') && !uri.startsWith('/api')) {
                    request.uri = '/index.html';
                  }
                  
                  return request;
                }`
              )
            }),
            eventType: cloudfront.FunctionEventType.VIEWER_REQUEST
          }
        ]
      },
      additionalBehaviors: {
        '/api/*': {
          origin: new origins.HttpOrigin(this.parseApiHost(props.apiEndpoint), {
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTPS_ONLY
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          compress: false
        }
      },
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
      logBucket: new s3.Bucket(this, 'DistributionLogBucket', {
        encryption: s3.BucketEncryption.S3_MANAGED,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
        blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
        objectOwnership: s3.ObjectOwnership.OBJECT_WRITER,
        accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE
      })
    });

    // Deploy placeholder frontend (in production, this would be built React app)
    new s3deploy.BucketDeployment(this, 'FrontendDeploy', {
      sources: [s3deploy.Source.asset(path.join(__dirname, '../../frontend/dist'))],
      destinationBucket: this.bucket,
      distributionPaths: ['/*'],
      distribution: this.distribution,
      prune: true
    });

    // Outputs
    new cdk.CfnOutput(this, 'DistributionUrl', {
      value: `https://${this.distribution.domainName}`,
      exportName: 'StockDebateFrontendUrl',
      description: 'CloudFront distribution URL for frontend'
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

  private parseApiHost(apiEndpoint: string): string {
    // Extract host from URL like https://xyz.execute-api.us-east-1.amazonaws.com/prod/
    // Handle both real URLs and CloudFormation tokens
    const endpointStr = apiEndpoint.toString();
    
    // If it's a token or path, extract the domain part
    if (endpointStr.includes('.execute-api.')) {
      const match = endpointStr.match(/https?:\/\/([^\/]+)/);
      if (match) {
        return match[1];
      }
    }
    
    // Fallback: try to parse as URL if possible
    try {
      const url = new URL(endpointStr);
      return url.hostname;
    } catch (e) {
      // If parsing fails, extract domain from the string pattern
      const match = endpointStr.match(/([a-zA-Z0-9-]+\.execute-api\.[a-z0-9-]+\.amazonaws\.com)/);
      return match ? match[1] : 'api.example.com';
    }
  }
}
