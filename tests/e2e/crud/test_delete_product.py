from http import HTTPStatus

import requests

from product.crud.dal.schemas.db import Product


def test_handler_204_success_delete(api_gw_url_slash_product: str, add_product_entry_to_db: Product) -> None:
    # when deleting an existing product, we get HTTP NO_CONTENT
    url_with_product_id = f'{api_gw_url_slash_product}/{add_product_entry_to_db.id}'
    response: requests.Response = requests.delete(url=url_with_product_id, timeout=10)
    assert response.status_code == HTTPStatus.NO_CONTENT

    # when deleting an already deleted product, we still get HTTP NO_CONTENT
    response = requests.delete(url=url_with_product_id, timeout=10)
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_handler_invalid_product_id(api_gw_url_slash_product: str) -> None:
    # when trying to delete a product with invalid id, you get HTTP BAD_REQUEST
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'
    response = requests.delete(url=url_with_product_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
