import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import { Construct } from 'constructs';
import { EcsServices } from './ecs-services';

export class StockDebateStack extends cdk.Stack {
  public vpc: ec2.Vpc;
  public cluster: ecs.Cluster;
  public alb: elbv2.ApplicationLoadBalancer;
  public database: rds.DatabaseInstance;
  public dbSecret: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const environment = process.env.ENV || 'dev';
    const isProd = environment === 'prod';

    cdk.Tags.of(this).add('Application', 'StockDebateAdvisor');
    cdk.Tags.of(this).add('Environment', environment);
    cdk.Tags.of(this).add('ManagedBy', 'CDK');

    // VPC
    this.vpc = new ec2.Vpc(this, 'StockDebateVpc', {
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 24,
          name: 'isolated',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
      maxAzs: isProd ? 3 : 2,
    });

    // Security Groups
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for ALB',
      allowAllOutbound: true,
    });
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), 'Allow HTTP');
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'Allow HTTPS');

    const ecsSecurityGroup = new ec2.SecurityGroup(this, 'ECSSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for ECS tasks',
      allowAllOutbound: true,
    });
    ecsSecurityGroup.addIngressRule(albSecurityGroup, ec2.Port.allTcp(), 'Allow from ALB');

    const dbSecurityGroup = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for RDS',
      allowAllOutbound: true,
    });
    dbSecurityGroup.addIngressRule(ecsSecurityGroup, ec2.Port.tcp(5432), 'Allow PostgreSQL');

    const redisSecurityGroup = new ec2.SecurityGroup(this, 'RedisSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for Redis',
      allowAllOutbound: true,
    });
    redisSecurityGroup.addIngressRule(ecsSecurityGroup, ec2.Port.tcp(6379), 'Allow Redis');

    // Database Secret
    this.dbSecret = new secretsmanager.Secret(this, 'DBSecret', {
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'stockdebate' }),
        generateStringKey: 'password',
        passwordLength: 32,
        excludeCharacters: '"@/\\',
      },
      description: 'RDS Master Password',
    });

    // RDS Database
    this.database = new rds.DatabaseInstance(this, 'StockDebateDB', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15_3,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE3,
        isProd ? ec2.InstanceSize.MEDIUM : ec2.InstanceSize.MICRO
      ),
      allocatedStorage: isProd ? 100 : 20,
      storageType: rds.StorageType.GP3,
      vpc: this.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      securityGroups: [dbSecurityGroup],
      credentials: rds.Credentials.fromSecret(this.dbSecret),
      databaseName: 'stock_debate',
      multiAz: isProd,
      backupRetention: cdk.Duration.days(isProd ? 30 : 7),
      deleteAutomatedBackups: !isProd,
      removalPolicy: isProd ? cdk.RemovalPolicy.SNAPSHOT : cdk.RemovalPolicy.DESTROY,
      iamAuthentication: true,
      cloudwatchLogsExports: ['postgresql'],
    });

    // Redis
    const redisSubnetGroup = new elasticache.CfnSubnetGroup(this, 'RedisSubnetGroup', {
      description: 'Subnet group for Redis cluster',
      subnetIds: this.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_ISOLATED }).subnetIds,
    });

    new elasticache.CfnCacheCluster(this, 'StockDebateRedis', {
      engine: 'redis',
      engineVersion: '7.0',
      cacheNodeType: isProd ? 'cache.r6g.large' : 'cache.t3.micro',
      numCacheNodes: isProd ? 3 : 1,
      vpcSecurityGroupIds: [redisSecurityGroup.securityGroupId],
      cacheSubnetGroupName: redisSubnetGroup.ref,
    });

    // S3 Buckets
    new s3.Bucket(this, 'AssetsBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    new s3.Bucket(this, 'BackupsBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // ECR Repositories
    ['backend', 'data-service', 'ai-service', 'frontend'].forEach(name => {
      new ecr.Repository(this, `${name}Repo`, {
        repositoryName: `stock-debate/${name}`,
        imageScanOnPush: true,
      });
    });

    // ECS Cluster
    this.cluster = new ecs.Cluster(this, 'StockDebateCluster', {
      vpc: this.vpc,
      clusterName: `stock-debate-${environment}`,
      containerInsights: true,
    });

    // CloudWatch Logs
    new logs.LogGroup(this, 'ECSLogGroup', {
      logGroupName: `/aws/ecs/stock-debate-${environment}`,
      retention: isProd ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // ALB
    this.alb = new elbv2.ApplicationLoadBalancer(this, 'StockDebateALB', {
      vpc: this.vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
      loadBalancerName: `stock-debate-alb-${environment}`,
    });

    // Listener
    const listener = this.alb.addListener('HTTPListener', {
      protocol: elbv2.ApplicationProtocol.HTTP,
      port: 80,
      open: true,
    });

    // Add ECS Services (Backend, Data Service, AI Service, Frontend)
    new EcsServices(this, 'EcsServices', {
      cluster: this.cluster,
      vpc: this.vpc,
      alb: this.alb,
      backendListener: listener,
      dbEndpoint: this.database.dbInstanceEndpointAddress,
      dbSecretArn: this.dbSecret.secretArn,
      ecsSecurityGroup: ecsSecurityGroup,
      environment,
      isProd,
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: this.vpc.vpcId,
      exportName: `${this.stackName}-VpcId`,
    });

    new cdk.CfnOutput(this, 'ALBUrl', {
      value: this.alb.loadBalancerDnsName,
      exportName: `${this.stackName}-ALBUrl`,
    });

    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.database.dbInstanceEndpointAddress,
      exportName: `${this.stackName}-DbEndpoint`,
    });

    new cdk.CfnOutput(this, 'ClusterName', {
      value: this.cluster.clusterName,
      exportName: `${this.stackName}-ClusterName`,
    });

    new cdk.CfnOutput(this, 'DatabaseSecretArn', {
      value: this.dbSecret.secretArn,
      exportName: `${this.stackName}-DbSecretArn`,
    });
  }
}
