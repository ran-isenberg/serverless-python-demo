from http import HTTPStatus

import requests

from product.crud.integration.schemas.db import Product


def test_handler_204_success_delete(api_gw_url_slash_product: str, add_product_entry_to_db: Product) -> None:
    # GIVEN a URL for deleting a product
    # AND a product entry existing in the database
    url_with_product_id = f'{api_gw_url_slash_product}/{add_product_entry_to_db.id}'

    # WHEN making a DELETE request to remove the existing product
    response: requests.Response = requests.delete(url=url_with_product_id, timeout=10)

    # THEN the response should indicate success with no content (HTTP 204)
    assert response.status_code == HTTPStatus.NO_CONTENT

    # AND WHEN making another DELETE request for the already deleted product
    response = requests.delete(url=url_with_product_id, timeout=10)

    # THEN the response should still indicate success with no content (HTTP 204)
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_handler_invalid_product_id(api_gw_url_slash_product: str) -> None:
    # GIVEN a URL for deleting a product
    # AND an invalid product ID
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'

    # WHEN making a DELETE request with the invalid product ID
    response = requests.delete(url=url_with_product_id)

    # THEN the response should indicate a bad request (HTTP 400)
    assert response.status_code == HTTPStatus.BAD_REQUEST
