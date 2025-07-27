#!/usr/bin/env python3
import os

import aws_cdk as cdk

from lambda_stack.lambda_stack import LambdaStack


app = cdk.App()

# Get context variables or use defaults
service_name = app.node.try_get_context("service_name") or "microservice-template"
environment = app.node.try_get_context("environment") or "dev"

# Create stack with dynamic name
stack_name = f"{service_name.title().replace('-', '')}{environment.title()}Stack"

LambdaStack(app, stack_name,
    service_name=service_name,
    env_name=environment,
    # Specify the AWS Region for deployment
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region='us-west-2'
    ),
    description=f"{service_name} - FastAPI Lambda with API Gateway ({environment})"
)

app.synth()
