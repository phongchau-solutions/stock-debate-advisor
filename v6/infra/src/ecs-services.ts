import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';

export interface EcsServicesProps {
  cluster: ecs.Cluster;
  vpc: ec2.Vpc;
  alb: elbv2.ApplicationLoadBalancer;
  backendListener: elbv2.ApplicationListener;
  dbEndpoint: string;
  dbSecretArn: string;
  ecsSecurityGroup: ec2.SecurityGroup;
  environment: string;
  isProd: boolean;
}

export class EcsServices extends cdk.Resource {
  constructor(scope: cdk.Stack, id: string, props: EcsServicesProps) {
    super(scope, id);

    // Create task execution role
    const taskExecutionRole = new iam.Role(scope, 'EcsTaskExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });

    taskExecutionRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
    );

    // Allow reading secrets
    taskExecutionRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'secretsmanager:GetSecretValue',
          'kms:Decrypt',
        ],
        resources: [props.dbSecretArn, 'arn:aws:kms:*:*:key/*'],
      })
    );

    // Create task role (for application permissions)
    const taskRole = new iam.Role(scope, 'EcsTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });

    // Backend Service
    const backendTaskDef = new ecs.FargateTaskDefinition(scope, 'BackendTaskDef', {
      memoryLimitMiB: props.isProd ? 2048 : 1024,
      cpu: props.isProd ? 1024 : 512,
      executionRole: taskExecutionRole,
      taskRole: taskRole,
    });

    const backendContainer = backendTaskDef.addContainer('backend', {
      image: ecs.ContainerImage.fromRegistry('node:18-alpine'),
      portMappings: [{ containerPort: 8000 }],
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'backend',
        logGroup: new logs.LogGroup(scope, 'BackendLogGroup', {
          logGroupName: `/ecs/stock-debate-backend-${props.environment}`,
          retention: props.isProd ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
          removalPolicy: cdk.RemovalPolicy.DESTROY,
        }),
      }),
      environment: {
        NODE_ENV: props.environment,
        PORT: '8000',
        DB_HOST: props.dbEndpoint,
        DB_PORT: '5432',
        DB_NAME: 'stock_debate',
        DATA_SERVICE_URL: 'http://data-service:8001',
        AI_SERVICE_URL: 'http://ai-service:8003',
      },
      secrets: {
        DB_USER: ecs.Secret.fromSecretsManager(
          cdk.aws_secretsmanager.Secret.fromSecretCompleteArn(scope, 'BackendDbSecret', props.dbSecretArn),
          'username'
        ),
        DB_PASSWORD: ecs.Secret.fromSecretsManager(
          cdk.aws_secretsmanager.Secret.fromSecretCompleteArn(scope, 'BackendDbSecret2', props.dbSecretArn),
          'password'
        ),
      },
    });

    // Backend ECS Service
    const backendService = new ecs.FargateService(scope, 'BackendService', {
      cluster: props.cluster,
      taskDefinition: backendTaskDef,
      desiredCount: props.isProd ? 3 : 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.ecsSecurityGroup],
    });

    // Add to ALB
    props.backendListener.addTargets('BackendTarget', {
      port: 8000,
      targets: [backendService],
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
      },
    });

    // Data Service Task Definition
    const dataServiceTaskDef = new ecs.FargateTaskDefinition(scope, 'DataServiceTaskDef', {
      memoryLimitMiB: props.isProd ? 2048 : 1024,
      cpu: props.isProd ? 1024 : 512,
      executionRole: taskExecutionRole,
      taskRole: taskRole,
    });

    dataServiceTaskDef.addContainer('data-service', {
      image: ecs.ContainerImage.fromRegistry('python:3.11-slim'),
      portMappings: [{ containerPort: 8001 }],
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'data-service',
        logGroup: new logs.LogGroup(scope, 'DataServiceLogGroup', {
          logGroupName: `/ecs/stock-debate-data-service-${props.environment}`,
          retention: props.isProd ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
          removalPolicy: cdk.RemovalPolicy.DESTROY,
        }),
      }),
      environment: {
        PORT: '8001',
        DB_HOST: props.dbEndpoint,
        DB_PORT: '5432',
        DB_NAME: 'stock_debate',
        LOCAL_DATA_MODE: 'true',
      },
      secrets: {
        DB_USER: ecs.Secret.fromSecretsManager(
          cdk.aws_secretsmanager.Secret.fromSecretCompleteArn(scope, 'DataServiceDbSecret', props.dbSecretArn),
          'username'
        ),
        DB_PASSWORD: ecs.Secret.fromSecretsManager(
          cdk.aws_secretsmanager.Secret.fromSecretCompleteArn(scope, 'DataServiceDbSecret2', props.dbSecretArn),
          'password'
        ),
      },
    });

    // Data Service ECS Service
    const dataService = new ecs.FargateService(scope, 'DataService', {
      cluster: props.cluster,
      taskDefinition: dataServiceTaskDef,
      desiredCount: props.isProd ? 2 : 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.ecsSecurityGroup],
    });

    // AI Service Task Definition
    const aiServiceTaskDef = new ecs.FargateTaskDefinition(scope, 'AIServiceTaskDef', {
      memoryLimitMiB: props.isProd ? 4096 : 2048,
      cpu: props.isProd ? 2048 : 1024,
      executionRole: taskExecutionRole,
      taskRole: taskRole,
    });

    aiServiceTaskDef.addContainer('ai-service', {
      image: ecs.ContainerImage.fromRegistry('python:3.11-slim'),
      portMappings: [{ containerPort: 8003 }],
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'ai-service',
        logGroup: new logs.LogGroup(scope, 'AIServiceLogGroup', {
          logGroupName: `/ecs/stock-debate-ai-service-${props.environment}`,
          retention: props.isProd ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
          removalPolicy: cdk.RemovalPolicy.DESTROY,
        }),
      }),
      environment: {
        PORT: '8003',
        PYTHONUNBUFFERED: '1',
      },
    });

    // AI Service ECS Service
    new ecs.FargateService(scope, 'AIService', {
      cluster: props.cluster,
      taskDefinition: aiServiceTaskDef,
      desiredCount: props.isProd ? 2 : 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.ecsSecurityGroup],
    });

    // Frontend Task Definition
    const frontendTaskDef = new ecs.FargateTaskDefinition(scope, 'FrontendTaskDef', {
      memoryLimitMiB: props.isProd ? 1024 : 512,
      cpu: props.isProd ? 512 : 256,
      executionRole: taskExecutionRole,
    });

    frontendTaskDef.addContainer('frontend', {
      image: ecs.ContainerImage.fromRegistry('node:18-alpine'),
      portMappings: [{ containerPort: 5174 }],
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'frontend',
        logGroup: new logs.LogGroup(scope, 'FrontendLogGroup', {
          logGroupName: `/ecs/stock-debate-frontend-${props.environment}`,
          retention: props.isProd ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
          removalPolicy: cdk.RemovalPolicy.DESTROY,
        }),
      }),
      environment: {
        VITE_API_BASE_URL: `http://backend:8000`,
      },
    });

    // Frontend ECS Service
    const frontendService = new ecs.FargateService(scope, 'FrontendService', {
      cluster: props.cluster,
      taskDefinition: frontendTaskDef,
      desiredCount: props.isProd ? 2 : 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.ecsSecurityGroup],
    });

    // Create target group for frontend
    const frontendTargetGroup = new elbv2.ApplicationTargetGroup(scope, 'FrontendTargetGroup', {
      vpc: props.vpc,
      protocol: elbv2.ApplicationProtocol.HTTP,
      port: 5174,
      targetType: elbv2.TargetType.IP,
      targets: [frontendService],
      healthCheck: {
        path: '/',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
      },
      targetGroupName: `stock-debate-frontend-${props.environment}`,
    });

    // Add frontend routing rule to ALB
    props.backendListener.addTargetGroups('FrontendRule', {
      priority: 1,
      targetGroups: [frontendTargetGroup],
      conditions: [elbv2.ListenerCondition.pathPatterns(['/', '/*'])],
    });
  }
}
