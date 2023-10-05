import json
from http import HTTPStatus
from typing import Any, Dict

import boto3

from product.crud.handlers.handle_create_product import handle_create_product
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def call_create_product_handler(body: Dict[str, Any]) -> Dict[str, Any]:
    return handle_create_product(body, generate_context())


def test_handler_200_ok(mocker, table_name: str) -> None:
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = handle_create_product(generate_api_gw_event(
        body=body.model_dump(),
        path_params={'product': product_id},
        product_id=product_id,
    ))
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
