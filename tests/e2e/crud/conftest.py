import json
from typing import Generator

import boto3
import pytest

from infrastructure.product.constants import (
    APIGATEWAY,
    IDENTITY_APP_CLIENT_ID_OUTPUT,
    IDENTITY_USER_POOL_ID_OUTPUT,
    PRODUCT_RESOURCE,
    PRODUCTS_RESOURCE,
    STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT,
    TABLE_NAME_OUTPUT,
    TEST_USER_IDENTITY_SECRET_NAME_OUTPUT,
)
from product.crud.models.product import Product
from tests.crud_utils import clear_table, generate_product_id
from tests.e2e.crud.utils import create_product, delete_product
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_product():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCT_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_products():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCTS_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api'


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()


@pytest.fixture(scope='module', autouse=True)
def table_name():
    return get_stack_output(TABLE_NAME_OUTPUT)


@pytest.fixture(scope='session')
def test_events_table():
    return get_stack_output(STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT)


@pytest.fixture()
def add_product_entry_to_db(api_gw_url_slash_product: str, table_name: str, id_token: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product_id = generate_product_id()
    product = Product(id=product_id, price=1, name='test')
    create_product(
        api_gw_url_slash_product=api_gw_url_slash_product, product_id=product_id, price=product.price, name=product.name, id_token=id_token
    )
    yield product
    delete_product(api_gw_url_slash_product, product_id, id_token)


@pytest.fixture(scope='session', autouse=True)
def id_token() -> Generator[str, None, None]:
    # Initialize boto3 client for Secrets Manager and Cognito Identity
    secrets_manager_client = boto3.client('secretsmanager')
    cognito_client = boto3.client('cognito-idp')

    # Name of the secret created in the previous CDK stack
    CLIENT_ID = get_stack_output(IDENTITY_APP_CLIENT_ID_OUTPUT)
    USER_POOL_ID = get_stack_output(IDENTITY_USER_POOL_ID_OUTPUT)
    SECRET_NAME = get_stack_output(TEST_USER_IDENTITY_SECRET_NAME_OUTPUT)

    response = secrets_manager_client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response['SecretString'])
    username = 'aabbaa'
    password = secret['password']

    email = 'aaaaaa@gmail.com'
    response = cognito_client.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=username,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email,
            },
            {'Name': 'email_verified', 'Value': 'True'},
        ],
        TemporaryPassword='Ini111111tial1$!',
    )

    cognito_client.admin_set_user_password(
        UserPoolId=USER_POOL_ID,
        Username=username,
        Password=password,
        Permanent=True,
    )
    # Use the credentials from the secret to login to the Cognito User Pool
    auth_response = cognito_client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={'USERNAME': username, 'PASSWORD': password},
        ClientId=CLIENT_ID,
    )
    yield auth_response['AuthenticationResult']['IdToken']
    cognito_client.admin_delete_user(UserPoolId=USER_POOL_ID, Username=username)
