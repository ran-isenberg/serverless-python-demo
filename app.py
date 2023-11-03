#!/usr/bin/env python3
import os

from aws_cdk import App, Environment
from boto3 import client, session

from infrastructure.product.product_stack import ServiceStack
from infrastructure.product.stack_utils import get_stack_name

account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name
environment = os.getenv('ENVIRONMENT', 'dev')
app = App()
my_stack = ServiceStack(
    app,
    get_stack_name(),
    env=Environment(account=os.environ.get('AWS_DEFAULT_ACCOUNT', account), region=os.environ.get('AWS_DEFAULT_REGION', region)),
    is_production=True if environment == 'production' else False,
)

app.synth()
