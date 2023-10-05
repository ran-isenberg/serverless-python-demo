from http import HTTPStatus

import requests

from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import GetProductOutput
from tests.crud_utils import generate_product_id


def test_handler_200_ok(api_gw_url_slash_product: str, add_product_entry_to_db: Product) -> None:
    # GIVEN a URL and an existing product in the database
    product_id = add_product_entry_to_db.id
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    expected_response = GetProductOutput(id=product_id, price=add_product_entry_to_db.price, name=add_product_entry_to_db.name)

    # WHEN making a GET request for the product
    response: requests.Response = requests.get(url=url_with_product_id, timeout=10)

    # THEN the response should be HTTP 200 OK
    # AND the response entry should match the expected response
    assert response.status_code == HTTPStatus.OK
    response_entry = GetProductOutput.model_validate_json(response.text)
    assert response_entry.model_dump() == expected_response.model_dump()


def test_handler_invalid_product_id(api_gw_url_slash_product: str) -> None:
    # GIVEN a URL with an invalid product ID
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'

    # WHEN making a GET request for the product
    response = requests.get(url=url_with_product_id)

    # THEN the response should indicate a bad request (HTTP 400)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_handler_product_does_not_exit(api_gw_url_slash_product: str) -> None:
    # GIVEN a URL with a valid but non-existing product ID
    product_id = generate_product_id()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'

    # WHEN making a GET request for the product
    response = requests.get(url=url_with_product_id)

    # THEN the response should indicate that the product is not found (HTTP 404)
    assert response.status_code == HTTPStatus.NOT_FOUND
