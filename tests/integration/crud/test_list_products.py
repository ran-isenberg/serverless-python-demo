from http import HTTPStatus
from typing import Any, Dict

from product.crud.handlers.list_products import list_products
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body
from tests.utils import generate_context


def call_delete_product(body: Dict[str, Any]) -> Dict[str, Any]:
    return list_products(body, generate_context())


def test_handler_200_ok():
    body = generate_create_product_request_body()
    response = call_delete_product(generate_api_gw_event(body=body.model_dump()))
    # assert response
    assert response['statusCode'] == HTTPStatus.NOT_IMPLEMENTED
