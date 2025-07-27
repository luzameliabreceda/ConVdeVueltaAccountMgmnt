import os
import json
import boto3
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct


class LambdaStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        service_name: str = "microservice-template",
        env_name: str = "dev",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.service_name = service_name
        self.env_name = env_name

        # Get secrets from Secrets Manager at build time
        secrets_environment_vars = self._get_secrets_environment_variables()

        # Lambda function for the FastAPI application
        api_lambda = _lambda.Function(
            self, f"{self.service_name.title().replace('-', '')}ApiFunction",
            function_name=f"{self.service_name}-api-{self.env_name}",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="src.lambda_handler.handler",
            code=_lambda.Code.from_asset(
                "..",
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_13.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r src/requirements.txt -t /asset-output && cp -au src/ /asset-output/"
                    ],
                }
            ),
            timeout=Duration.seconds(30),
            memory_size=512 if self.env_name == "dev" else 1024,
            environment={
                "ENVIRONMENT": self.env_name,
                "SERVICE_NAME": self.service_name,
                **secrets_environment_vars,
            },
            log_retention=logs.RetentionDays.THREE_DAYS if self.env_name == "dev" else logs.RetentionDays.ONE_WEEK,
        )

        # API Gateway for the Lambda function
        api = apigateway.LambdaRestApi(
            self, f"{self.service_name.title().replace('-', '')}ApiGateway",
            handler=api_lambda,
            proxy=True,
            description=f"{self.service_name} API - {self.env_name}",
            deploy_options={
                "stage_name": self.env_name,
                "throttling_rate_limit": 100 if self.env_name == "dev" else 1000,
                "throttling_burst_limit": 200 if self.env_name == "dev" else 2000,
            }
        )

        # CloudFormation Outputs
        CfnOutput(
            self, "ApiGatewayUrl",
            value=api.url,
            description="API Gateway endpoint URL"
        )

        CfnOutput(
            self, "LambdaFunctionArn",
            value=api_lambda.function_arn,
            description="Lambda Function ARN"
        )

    def _get_secrets_environment_variables(self) -> dict:
        """
        Get secrets from Secrets Manager at build time and return them as environment variables.
        The secrets are expected to be in JSON format and will be flattened as env vars.
        """
        secret_name = f"cvdv-secrets-{self.env_name}"
        
        try:
            # Create Secrets Manager client
            secrets_client = boto3.client('secretsmanager')
            
            # Get the secret value
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            
            # Parse the JSON secret
            secrets_dict = json.loads(secret_string)
            
            # Return the secrets exactly as they are in the JSON
            # No modifications to keys or values
            env_vars = {}
            for key, value in secrets_dict.items():
                env_vars[key] = value  # Keep original key and value
                print(f"Setting environment variable: {key}")
            
            return env_vars
            
        except Exception as e:
            print(f"Error fetching secrets from Secrets Manager: {str(e)}")
            print(f"Secret name: {secret_name}")
            return {}
