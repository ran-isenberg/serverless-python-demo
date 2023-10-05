import json
from http import HTTPStatus
from typing import Generator

import boto3
import pytest
from botocore.stub import Stubber

from product.crud.handlers.handle_delete_product import handle_delete_product
from product.crud.integration.dynamo_dal_handler import DynamoDalHandler
from product.crud.integration.schemas.db import Product
from tests.crud_utils import generate_api_gw_event, generate_product_id
from tests.utils import generate_context


@pytest.fixture()
def add_product_entry_to_db(table_name: str) -> Generator[Product, None, None]:
    product = Product(id=generate_product_id(), price=1, name='test')
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield product
    table.delete_item(Key={'id': product.id})


def test_handler_204_success_delete(add_product_entry_to_db: Product):
    product_id = add_product_entry_to_db.id
    event = generate_api_gw_event(path_params={'product': product_id})
    response = handle_delete_product(event, generate_context())
    # assert response
    assert response['statusCode'] == HTTPStatus.NO_CONTENT


def test_internal_server_error(table_name):
    # when a DynamoDB exception is raised, internal server error is returned
    db_handler: DynamoDalHandler = DynamoDalHandler(table_name)
    table = db_handler._get_db_handler(table_name)

    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='delete_item', service_error_code='ValidationException')
        event = generate_api_gw_event(path_params={'product': generate_product_id()})
        response = handle_delete_product(event, generate_context())

    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR


def test_handler_bad_request_invalid_path_params():
    # when calling the API with incorrect path params, you get an HTTP bad request error code
    event = generate_api_gw_event(path_params={'dummy': generate_product_id()})
    response = handle_delete_product(event, generate_context())
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}
