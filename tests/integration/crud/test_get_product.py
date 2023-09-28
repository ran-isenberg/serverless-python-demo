import json
from http import HTTPStatus
from typing import Generator

import boto3
import pytest
from botocore.stub import Stubber

from product.crud.dal.dynamo_dal_handler import DynamoDalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.get_product import get_product
from product.crud.schemas.output import GetProductOutput
from tests.crud_utils import generate_api_gw_event, generate_product_id
from tests.utils import generate_context


@pytest.fixture()
def add_product_entry_to_db(table_name: str) -> Generator[ProductEntry, None, None]:
    product = ProductEntry(id=generate_product_id(), price=1, name='test')
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield product
    table.delete_item(Key={'id': product.id})


def test_handler_200_ok(add_product_entry_to_db: ProductEntry):
    # when adding a new product and then trying to get it, the product is returned correctly
    product_id = add_product_entry_to_db.id
    event = generate_api_gw_event(path_params={'product': product_id})
    response = get_product(event, generate_context())
    # assert response
    assert response['statusCode'] == HTTPStatus.OK
    response_entry = GetProductOutput.model_validate_json(response['body'])
    assert response_entry.model_dump() == add_product_entry_to_db.model_dump()


def test_internal_server_error(table_name):
    # when a DynamoDB exception is raised, internal server error is returned
    db_handler: DynamoDalHandler = DynamoDalHandler(table_name)
    table = db_handler._get_db_handler(table_name)

    with Stubber(table.meta.client) as stubber:
        stubber.add_client_error(method='get_item', service_error_code='ValidationException')
        event = generate_api_gw_event(path_params={'product': generate_product_id()})
        response = get_product(event, generate_context())

    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR


def test_handler_bad_request_invalid_path_params():
    # when calling the API with incorrect path params, you get an HTTP bad request error code
    event = generate_api_gw_event(path_params={'dummy': generate_product_id()})
    response = get_product(event, generate_context())
    assert response['statusCode'] == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response['body'])
    assert body_dict == {}
