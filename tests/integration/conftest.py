import json
import os
from datetime import datetime
from typing import Generator

import boto3
import pytest

from infrastructure.product.constants import (
    IDEMPOTENCY_TABLE_NAME_OUTPUT,
    IDENTITY_APP_CLIENT_ID_OUTPUT,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
    TABLE_NAME_OUTPUT,
    TEST_USER_IDENTITY_SECRET_NAME_OUTPUT,
)
from product.crud.models.product import Product
from product.models.products.product import ProductEntry
from tests.crud_utils import clear_table, generate_product_id
from tests.utils import get_stack_output


@pytest.fixture(scope='session', autouse=True)
def init():
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'
    os.environ['AWS_DEFAULT_REGION'] = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')  # used for appconfig mocked boto calls
    os.environ['TABLE_NAME'] = get_stack_output(TABLE_NAME_OUTPUT)
    os.environ['IDEMPOTENCY_TABLE_NAME'] = get_stack_output(IDEMPOTENCY_TABLE_NAME_OUTPUT)


@pytest.fixture(scope='session', autouse=True)
def table_name():
    return os.environ['TABLE_NAME']


@pytest.fixture(scope='module', autouse=True)
def add_product_entry_to_db(table_name: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product = ProductEntry(id=generate_product_id(), price=1, name='test', created_at=int(datetime.utcnow().timestamp()))
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield Product(id=product.id, name=product.name, price=product.price)
    table.delete_item(Key={'id': product.id})


@pytest.fixture(scope='session', autouse=True)
def access_token() -> str:
    # Initialize boto3 client for Secrets Manager and Cognito Identity
    secrets_manager_client = boto3.client('secretsmanager')
    cognito_client = boto3.client('cognito-idp')

    # Name of the secret created in the previous CDK stack
    SECRET_NAME = get_stack_output(TEST_USER_IDENTITY_SECRET_NAME_OUTPUT)
    CLIENT_ID = get_stack_output(IDENTITY_APP_CLIENT_ID_OUTPUT)

    # Retrieve secret from Secrets Manager
    response = secrets_manager_client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response['SecretString'])

    # Use the credentials from the secret to login to the Cognito User Pool
    try:
        auth_response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': secret['username'], 'PASSWORD': secret['password']},
            ClientId=CLIENT_ID,
        )
        # Extract JWT tokens
        # id_token = auth_response['AuthenticationResult']['IdToken']
        access_token = auth_response['AuthenticationResult']['AccessToken']
        # refresh_token = auth_response['AuthenticationResult']['RefreshToken']
        return access_token
    except cognito_client.exceptions.NotAuthorizedException:
        print('Invalid credentials')
    except cognito_client.exceptions.UserNotConfirmedException:
        print('User not confirmed')
    except Exception as e:
        print(f'An error occurred: {e}')
