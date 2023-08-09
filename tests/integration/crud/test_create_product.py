import json
from http import HTTPStatus
from typing import Any, Dict

import boto3
from botocore.stub import Stubber

from service.crud.dal.dynamo_dal_handler import DynamoDalHandler
from service.crud.schemas.input import CreateProductRequest
from tests.utils import generate_api_gw_event, generate_context, generate_product_id, generate_random_string


def call_create_product(body: Dict[str, Any]) -> Dict[str, Any]:
    # important is done here since idempotency decorator requires an env. variable during import time
    # conf.test sets that env. variable (table name) but it runs after imports
    # this way, idempotency import runs after conftest sets the values already
    from service.crud.handlers.create_product import create_product
    return create_product(body, generate_context())


def test_handler_200_ok(mocker, table_name: str):
    product_name = generate_random_string()
    price = 5
    product_id = generate_product_id()
    body = CreateProductRequest(id=product_id, name=product_name, price=price)
    response = call_create_product(generate_api_gw_event(body.model_dump()))
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['id'] == product_id
    # assert side effect - DynamoDB table
    dynamodb_table = boto3.resource('dynamodb').Table(table_name)
    response = dynamodb_table.get_item(Key={'id': body_dict['id']})
    assert 'Item' in response  # product was found
    assert response['Item']['name'] == product_name
    assert response['Item']['price'] == price
    assert response['Item']['id'] == product_id


def test_internal_server_error():
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler()
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    product_name = generate_random_string()
    price = 5
    product_id = generate_product_id()
    body = CreateProductRequest(id=product_id, name=product_name, price=price)
    response = call_create_product(generate_api_gw_event(body.model_dump()))
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    stubber.deactivate()
    DynamoDalHandler._instances = {}


def test_handler_bad_request():
    response = call_create_product(generate_api_gw_event({'price': 5}))
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}
