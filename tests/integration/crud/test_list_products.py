from http import HTTPStatus
from typing import Generator

import boto3
import pytest
from botocore.stub import Stubber

from product.crud.handlers.handle_list_products import handle_list_products
from product.crud.integration.dynamo_dal_handler import DynamoDalHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import ListProductsOutput
from tests.crud_utils import clear_table, generate_api_gw_list_products_event, generate_product_id
from tests.utils import generate_context


@pytest.fixture()
def add_product_entry_to_db(table_name: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product = Product(id=generate_product_id(), price=1, name='test')
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield product
    table.delete_item(Key={'id': product.id})


def test_handler_200_ok(add_product_entry_to_db: Product):
    # when adding one product to the table and listing it, one item is returned
    event = generate_api_gw_list_products_event()
    response = handle_list_products(event, generate_context())
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = ListProductsOutput.model_validate_json(response['body'])
    products = response_entry.products
    # we cleared the table so only one product
    assert len(products) == 1
    # assert we got the item we expect
    assert products[0].model_dump() == add_product_entry_to_db.model_dump()


def test_handler_empty_list(table_name: str):
    # when listing an empty table, an empty list of products is returned
    clear_table(table_name)
    event = generate_api_gw_list_products_event()
    response = handle_list_products(event, generate_context())
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = ListProductsOutput.model_validate_json(response['body'])
    products = response_entry.products
    assert not products


def test_internal_server_error(table_name):
    # when a DynamoDB exception is raised, internal server error is returned
    db_handler: DynamoDalHandler = DynamoDalHandler(table_name)
    table = db_handler._get_db_handler(table_name)

    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='scan', service_error_code='ValidationException')
        event = generate_api_gw_list_products_event()
        response = handle_list_products(event, generate_context())

    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR
