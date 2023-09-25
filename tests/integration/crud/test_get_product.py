from http import HTTPStatus
from typing import Any, Dict

from product.crud.handlers.get_product import get_product
from tests.crud_utils import generate_api_gw_event, generate_create_product_request_body, generate_product_id
from tests.utils import generate_context


def call_delete_product(body: Dict[str, Any]) -> Dict[str, Any]:
    return get_product(body, generate_context())


def test_handler_200_ok():
    body = generate_create_product_request_body()
    product_id = generate_product_id()
    response = call_delete_product(generate_api_gw_event(body=body.model_dump(), path_params={'product': product_id}))
    # assert response
    assert response['statusCode'] == HTTPStatus.NOT_IMPLEMENTED
