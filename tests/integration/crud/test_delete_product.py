from http import HTTPMethod, HTTPStatus

from botocore.stub import Stubber

from product.crud.handlers.handle_delete_product import lambda_handler
from product.crud.integration.dynamo_db_handler import DynamoDbHandler
from product.crud.integration.schemas.db import Product
from tests.crud_utils import generate_product_api_gw_event, generate_product_id
from tests.utils import generate_context


def test_handler_204_success_delete(add_product_entry_to_db: Product):
    # GIVEN a product entry in the database
    product_id = add_product_entry_to_db.id

    # WHEN requesting to delete the product
    event = generate_product_api_gw_event(http_method=HTTPMethod.DELETE, product_id=product_id, path_params={'product': product_id})
    response = lambda_handler(event, generate_context())

    # THEN the response should indicate successful deletion (HTTP 204 No Content)
    assert response['statusCode'] == HTTPStatus.NO_CONTENT


def test_internal_server_error(table_name):
    # GIVEN a DynamoDB exception scenario
    db_handler: DynamoDbHandler = DynamoDbHandler(table_name)
    table = db_handler._get_db_handler(table_name)

    with Stubber(table.meta.client) as stubber:
        # WHEN attempting to delete a product while the DynamoDB exception is triggered
        stubber.add_client_error(method='delete_item', service_error_code='ValidationException')
        product_id = generate_product_id()
        event = generate_product_api_gw_event(http_method=HTTPMethod.DELETE, product_id=product_id, path_params={'product': product_id})
        response = lambda_handler(event, generate_context())

    # THEN the response should indicate an internal server error (HTTP 500 Internal Server Error)
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR


def test_handler_bad_request_invalid_path_params():
    # GIVEN an invalid request with incorrect path parameters
    product_id = generate_product_id()

    # WHEN requesting to delete the product
    event = generate_product_api_gw_event(http_method=HTTPMethod.DELETE, product_id=product_id, path_params={'dummy': product_id}, path='dummy')
    response = lambda_handler(event, generate_context())

    # THEN the response should indicate invalid path parameters (HTTP Not Found)
    assert response['statusCode'] == HTTPStatus.NOT_FOUND
