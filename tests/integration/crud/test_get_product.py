import json
from http import HTTPMethod, HTTPStatus

from botocore.stub import Stubber

from product.crud.handlers.handle_get_product import lambda_handler
from product.crud.integration.dynamo_db_handler import DynamoDbHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import GetProductOutput
from tests.crud_utils import generate_product_api_gw_event, generate_product_id
from tests.utils import generate_context


def test_handler_200_ok(add_product_entry_to_db: Product):
    # GIVEN a product entry in the database
    product_id = add_product_entry_to_db.id

    # WHEN requesting the product details
    event = generate_product_api_gw_event(http_method=HTTPMethod.GET, product_id=product_id, path_params={'product': product_id})
    response = lambda_handler(event, generate_context())

    # THEN the response should return OK (HTTP 200) and match the product entry in the database
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = GetProductOutput.model_validate_json(response['body'])
    assert response_entry.model_dump() == add_product_entry_to_db.model_dump()


def test_internal_server_error(table_name):
    # GIVEN a DynamoDB exception scenario
    db_handler: DynamoDbHandler = DynamoDbHandler(table_name)
    table = db_handler._get_table(table_name)

    with Stubber(table.meta.client) as stubber:
        # WHEN attempting to get a product while the DynamoDB exception is triggered
        stubber.add_client_error(method='get_item', service_error_code='ValidationException')
        product_id = generate_product_id()
        event = generate_product_api_gw_event(http_method=HTTPMethod.GET, product_id=product_id, path_params={'product': product_id})
        response = lambda_handler(event, generate_context())

    # THEN the response should indicate an internal server error (HTTP 500 Internal Server Error)
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR


def test_handler_bad_request_invalid_path_params():
    # GIVEN an invalid request with incorrect path parameters
    product_id = generate_product_id()

    # WHEN requesting the product details
    event = generate_product_api_gw_event(http_method=HTTPMethod.GET, product_id=product_id, path_params={'dummy': product_id}, path='dummy')
    response = lambda_handler(event, generate_context())

    # THEN the response should indicate invalid path parameters (HTTP Not Found)
    assert response['statusCode'] == HTTPStatus.NOT_FOUND


def test_handler_product_not_found():
    # GIVEN an valid request with a non existent product id
    product_id = generate_product_id()

    # WHEN requesting the product details
    event = generate_product_api_gw_event(http_method=HTTPMethod.GET, product_id=product_id, path_params={'product': product_id})
    response = lambda_handler(event, generate_context())

    # THEN the response should indicate (HTTP Not Found)
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'product was not found'


def test_handler_bad_request_invalid_product_id():
    # GIVEN an invalid product creation request with an invalid product id
    product_id = 'aaaaaa'
    # WHEN the lambda handler processes the request
    response = lambda_handler(
        event=generate_product_api_gw_event(http_method=HTTPMethod.GET, product_id=product_id, path_params={'product': product_id}),
        context=generate_context(),
    )

    # THEN the response should indicate bad request due to invalid input (HTTP 400 Bad Request)
    # AND contain an appropriate error message
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict['error'] == 'invalid input'
