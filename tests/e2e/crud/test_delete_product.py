from http import HTTPStatus

import requests

from product.crud.models.product import Product
from tests.crud_utils import generate_product_id
from tests.e2e.crud.utils import get_auth_header


def test_handler_204_success_delete(api_gw_url_slash_product: str, add_product_entry_to_db: Product, id_token: str) -> None:
    # GIVEN a URL for deleting a product
    # AND a product entry existing in the database
    url_with_product_id = f'{api_gw_url_slash_product}/{add_product_entry_to_db.id}'

    # WHEN making a DELETE request to remove the existing product
    response: requests.Response = requests.delete(url=url_with_product_id, timeout=10, headers=get_auth_header(id_token))

    # THEN the response should indicate success with no content (HTTP 204)
    assert response.status_code == HTTPStatus.NO_CONTENT

    # AND WHEN making another DELETE request for the already deleted product
    response = requests.delete(url=url_with_product_id, timeout=10, headers=get_auth_header(id_token))

    # THEN the response should still indicate success with no content (HTTP 204)
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_handler_invalid_product_id(api_gw_url_slash_product: str, id_token: str) -> None:
    # GIVEN a URL for deleting a product
    # AND an invalid product ID
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'

    # WHEN making a DELETE request with the invalid product ID
    response = requests.delete(url=url_with_product_id, headers=get_auth_header(id_token))

    # THEN the response should indicate a bad request (HTTP 400)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_handler_invalid_auth_token(api_gw_url_slash_product: str) -> None:
    # GIVEN a URL for deleting a product
    url_with_product_id = f'{api_gw_url_slash_product}/{generate_product_id()}'

    # WHEN making a DELETE request with an invalid id token
    response = requests.delete(url=url_with_product_id, headers=get_auth_header('aaaa'))

    # THEN the response should indicate an authorized request (HTTP 401)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
