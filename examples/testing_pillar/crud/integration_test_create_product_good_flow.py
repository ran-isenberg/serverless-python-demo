import json
from http import HTTPStatus

import boto3

from product.crud.handlers.handle_create_product import lambda_handler
from tests.crud_utils import generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def test_handler_200_ok(mocker, table_name: str) -> None:
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = lambda_handler({}, generate_context())
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
