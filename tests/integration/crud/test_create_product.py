import json
from datetime import datetime
from http import HTTPMethod, HTTPStatus

import boto3
from botocore.stub import Stubber

from product.crud.integration.dynamo_db_handler import DynamoDbHandler
from product.crud.models.product import Product
from tests.crud_utils import generate_create_product_request_body, generate_product_api_gw_event, generate_product_id
from tests.utils import generate_context


def call_handler(event, context):
    from product.crud.handlers.handle_create_product import lambda_handler
    return lambda_handler(event, context)


def test_handler_200_ok(monkeypatch, table_name: str):
    # Set POWERTOOLS_IDEMPOTENCY_DISABLED before calling decorated functions
    monkeypatch.setenv('POWERTOOLS_IDEMPOTENCY_DISABLED', 1)
    # GIVEN a product creation request
    body = generate_create_product_request_body()
    product_id = generate_product_id()

    # WHEN the lambda handler processes the request
    response = call_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body=body.model_dump(),
                                            path_params={'product': product_id}),
        context=generate_context(),
    )

    # THEN the response should indicate successful creation (HTTP 200 OK) and contain correct product data
    assert response['statusCode'] == HTTPStatus.OK
    body_dict = json.loads(response['body'])
    assert body_dict['id'] == product_id

    # AND the DynamoDB table should contain the new product with correct data
    dynamodb_table = boto3.resource('dynamodb').Table(table_name)
    response = dynamodb_table.get_item(Key={'id': product_id})
    assert 'Item' in response
    assert response['Item']['name'] == body.name
    assert response['Item']['price'] == body.price
    assert response['Item']['id'] == product_id
    now = int(datetime.utcnow().timestamp())
    assert now - int(response['Item']['created_at']) <= 60  # assume item was created in last minute, check that utc time calc is correct


def test_handler_bad_request_product_already_exists(add_product_entry_to_db: Product):
    # GIVEN a product that already exists in the database
    product_id = add_product_entry_to_db.id

    # WHEN attempting to create a product with the same ID
    response = call_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body=add_product_entry_to_db.model_dump(),
                                            path_params={'product': product_id}),
        context=generate_context(),
    )

    # THEN the response should indicate a bad request due to existing product (HTTP 400 Bad Request)
    # AND contain an appropriate error message
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'product already exists'


def test_internal_server_error(table_name: str):
    # GIVEN a DynamoDB exception scenario
    db_handler: DynamoDbHandler = DynamoDbHandler(table_name)
    table = db_handler._get_table(table_name)

    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='put_item', service_error_code='ValidationException')
        body = generate_create_product_request_body()
        product_id = generate_product_id()

        # WHEN attempting to create a product while the DynamoDB exception is triggered
        response = call_handler(
            event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body=body.model_dump(),
                                                path_params={'product': product_id}),
            context=generate_context(),
        )

    # THEN the response should indicate an internal server error (HTTP 500 Internal Server Error)
    # AND contain an appropriate error message
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'internal server error'


def test_handler_bad_request_invalid_body_input():
    # GIVEN an invalid product creation request with insufficient body input
    product_id = generate_product_id()

    # WHEN the lambda handler processes the request
    response = call_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body={'price': 5},
                                            path_params={'product': product_id}),
        context=generate_context(),
    )

    # THEN the response should indicate bad request due to invalid input (HTTP 400 Bad Request)
    # AND contain an appropriate error message
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'invalid input'


def test_handler_bad_request_invalid_product_id():
    # GIVEN an invalid product creation request with an invalid product id
    product_id = 'aaaaaa'
    body = generate_create_product_request_body()
    # WHEN the lambda handler processes the request
    response = call_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body=body.model_dump(),
                                            path_params={'product': product_id}),
        context=generate_context(),
    )

    # THEN the response should indicate bad request due to invalid input (HTTP 400 Bad Request)
    # AND contain an appropriate error message
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'invalid input'


def test_handler_bad_request_invalid_path_params():
    # GIVEN an invalid product creation request with incorrect path parameters
    body = generate_create_product_request_body()
    product_id = generate_product_id()

    # WHEN the lambda handler processes the request
    response = call_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.PUT, product_id=product_id, body=body.model_dump(),
                                            path_params={'dummy': product_id}, path='dummy'),
        context=generate_context(),
    )

    # THEN the response should indicate a not found error (HTTP 404 Not Found)
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
