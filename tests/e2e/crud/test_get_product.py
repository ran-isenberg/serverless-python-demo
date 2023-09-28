from http import HTTPStatus

import requests

from product.crud.dal.schemas.db import ProductEntry
from product.crud.schemas.output import GetProductOutput
from tests.crud_utils import generate_product_id


def test_handler_200_ok(api_gw_url_slash_product: str, add_product_entry_to_db: ProductEntry) -> None:
    # when trying to get an existing, we get HTTP 200 OK and its fields match the created product
    product_id = add_product_entry_to_db.id
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response: requests.Response = requests.get(url=url_with_product_id, timeout=10)
    assert response.status_code == HTTPStatus.OK
    expected_response = GetProductOutput(id=product_id, price=add_product_entry_to_db.price, name=add_product_entry_to_db.name)
    response_entry = GetProductOutput.model_validate_json(response.text)
    assert response_entry.model_dump() == expected_response.model_dump()


def test_handler_invalid_product_id(api_gw_url_slash_product: str) -> None:
    # when trying to get a product with invalid id, you get HTTP BAD_REQUEST
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'
    response = requests.get(url=url_with_product_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_handler_product_does_not_exit(api_gw_url_slash_product: str) -> None:
    # when trying to get a product with valid id but it does not exist, you get HTTP NOT_FOUND
    product_id = generate_product_id()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.get(url=url_with_product_id)
    assert response.status_code == HTTPStatus.NOT_FOUND
