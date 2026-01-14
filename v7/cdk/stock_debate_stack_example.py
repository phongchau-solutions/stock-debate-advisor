"""Python CDK"""

from aws_cdk import cdk, aws_lambda as lambda_, aws_dynamodb as dynamodb, aws_apigateway as apigateway, aws_iam as iam  # type: ignore
from constructs import Construct  # type: ignore


class StockDebateStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        env, p = (
            self.node.try_get_context("environment") or "dev",
            self.node.try_get_context("stackPrefix") or "SD",
        )
        
        # DynamoDB
        tbl = dynamodb.Table(self, f"{p}DB", table_name=f"{p}-tbl-{env}",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST, removal_policy=cdk.RemovalPolicy.DESTROY)
        
        # Lambda
        fn = lambda_.Function(self, f"{p}Fn", function_name=f"{p}-fn-{env}", runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler", code=lambda_.Code.from_asset("../../ai-service/lambda"),
            environment={"TABLE": tbl.table_name}, timeout=cdk.Duration.seconds(900), memory_size=512)
        tbl.grant_read_write_data(fn)
        fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"], 
                resources=["arn:aws:bedrock:*::foundation-model/*"]
            )
        )
        
        # API
        api = apigateway.RestApi(self, f"{p}API",
            default_cors_preflight_options=apigateway.CorsOptions(allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=apigateway.Cors.ALL_METHODS, allow_headers=["Content-Type"]))
        api.root.add_resource("debates").add_method(
            "POST", apigateway.LambdaIntegration(fn)
        )
        api.root.add_resource("data").add_resource("{id}").add_method(
            "GET", apigateway.LambdaIntegration(fn)
        )

        # Outputs
        cdk.CfnOutput(self, "API", value=api.url)
        cdk.CfnOutput(self, "Table", value=tbl.table_name)
