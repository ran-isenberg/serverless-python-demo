import random
import string

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

from infrastructure.product.utils import get_stack_name


def generate_random_string(length: int = 7):
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


def generate_context() -> LambdaContext:
    context = LambdaContext()
    context._aws_request_id = '888888'
    return context


def generate_random_integer():
    return random.randint(1, 10000)


def get_stack_output(output_key: str) -> str:
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=get_stack_name())
    stack_outputs = response['Stacks'][0]['Outputs']
    for value in stack_outputs:
        if str(value['OutputKey']) == output_key:
            return value['OutputValue']
    raise Exception(f'stack output {output_key} was not found')
