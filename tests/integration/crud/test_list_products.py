from http import HTTPStatus

from botocore.stub import Stubber

from product.crud.handlers.handle_list_products import lambda_handler
from product.crud.integration.dynamo_db_handler import DynamoDbHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import ListProductsOutput
from tests.crud_utils import clear_table, generate_api_gw_list_products_event
from tests.utils import generate_context


def test_handler_200_ok(add_product_entry_to_db: Product):
    # GIVEN a product entry in the database
    event = generate_api_gw_list_products_event()

    # WHEN listing all products
    response = lambda_handler(event, generate_context())

    # THEN the response should return OK (HTTP 200)
    # AND contain exactly one product, which matches the added product entry
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = ListProductsOutput.model_validate_json(response['body'])
    products = response_entry.products
    assert len(products) == 1
    assert products[0].model_dump() == add_product_entry_to_db.model_dump()


def test_handler_empty_list(table_name: str):
    # GIVEN an empty product table
    clear_table(table_name)

    # WHEN listing all products
    event = generate_api_gw_list_products_event()
    response = lambda_handler(event, generate_context())

    # THEN the response should return OK (HTTP 200)
    # AND the product list should be empty
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = ListProductsOutput.model_validate_json(response['body'])
    products = response_entry.products
    assert not products


def test_internal_server_error(table_name):
    # GIVEN a DynamoDB exception scenario
    db_handler: DynamoDbHandler = DynamoDbHandler(table_name)
    table = db_handler._get_db_handler(table_name)

    with Stubber(table.meta.client) as stubber:
        # WHEN attempting to list products while the DynamoDB exception is triggered
        stubber.add_client_error(method='scan', service_error_code='ValidationException')
        event = generate_api_gw_list_products_event()
        response = lambda_handler(event, generate_context())

    # THEN the response should indicate an internal server error (HTTP 500)
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
