import json
from http import HTTPStatus

import boto3
from botocore.stub import Stubber

from product.crud.handlers.handle_create_product import lambda_handler
from product.crud.integration.dynamo_dal_handler import DynamoDalHandler
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def test_handler_200_ok(table_name: str):
    # when sending a create product request, we expect its output to match the DynamoDB item
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = lambda_handler(
        event=generate_api_gw_event(product_id=product_id, body=body.model_dump(), path_params={'product': product_id}),
        context=generate_context(),
    )
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


def test_internal_server_error(table_name: str):
    # when a DynamoDB exception is raised, internal server error is returned
    db_handler: DynamoDalHandler = DynamoDalHandler(table_name)
    table = db_handler._get_db_handler(table_name)
    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='put_item', service_error_code='ValidationException')
        body = generate_create_product_request_body()
        product_id = generate_product_id()
        response = lambda_handler(
            event=generate_api_gw_event(product_id=product_id, body=body.model_dump(), path_params={'product': product_id}),
            context=generate_context(),
        )
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'internal server error'


def test_handler_bad_request_invalid_body_input():
    # when sending a request with invalid body payload, we get HTTP bad request status code
    product_id = generate_product_id()
    response = lambda_handler(
        event=generate_api_gw_event(product_id=product_id, body={'price': 5}, path_params={'product': product_id}),
        context=generate_context(),
    )
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'invalid input'


def test_handler_bad_request_invalid_path_params():
    # when sending a request with invalid path params, we get HTTP bad request status code
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = lambda_handler(
        event=generate_api_gw_event(product_id=product_id, body=body.model_dump(), path_params={'dummy': product_id}, path='dummy'),
        context=generate_context(),
    )
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
