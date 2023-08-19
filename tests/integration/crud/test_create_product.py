import json
from http import HTTPStatus
from typing import Any, Dict

import boto3
from botocore.stub import Stubber

from product.crud.dal.dynamo_dal_handler import DynamoDalHandler
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def call_create_product(body: Dict[str, Any]) -> Dict[str, Any]:
    # important is done here since idempotency decorator requires an env. variable during import time
    # conf.test sets that env. variable (table name) but it runs after imports
    # this way, idempotency import runs after conftest sets the values already
    from product.crud.handlers.create_product import create_product
    return create_product(body, generate_context())


def test_handler_200_ok(mocker, table_name: str):
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = call_create_product(generate_api_gw_event(body=body.model_dump(), path_params={'product': product_id}))
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['id'] == product_id
    # assert side effect - DynamoDB table
    dynamodb_table = boto3.resource('dynamodb').Table(table_name)
    response = dynamodb_table.get_item(Key={'id': product_id})
    assert 'Item' in response  # product was found
    assert response['Item']['name'] == body.name
    assert response['Item']['price'] == body.price
    assert response['Item']['id'] == product_id


def test_internal_server_error():
    db_handler: DynamoDalHandler = DynamoDalHandler('table')
    table = db_handler._get_db_handler()
    stubber = Stubber(table.meta.client)
    stubber.add_client_error(method='put_item', service_error_code='ValidationException')
    stubber.activate()
    body = generate_create_product_request_body()
    response = call_create_product(generate_api_gw_event(body=body.model_dump(), path_params={'product': generate_product_id()}))
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    stubber.deactivate()
    DynamoDalHandler._instances = {}


def test_handler_bad_request_invalid_body():
    response = call_create_product(generate_api_gw_event({'price': 5}, path_params={'product': generate_product_id()}))
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}


def test_handler_bad_request_invalid_path_params():
    body = generate_create_product_request_body()
    response = call_create_product(generate_api_gw_event(body=body.model_dump(), path_params={'dummy': generate_product_id()}))
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}
