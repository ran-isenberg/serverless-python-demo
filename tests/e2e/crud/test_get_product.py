from http import HTTPStatus

import requests


def test_handler_200_ok(api_gw_url_slash_product: str, product_id: str):
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.get(url=url_with_product_id, timeout=10)
    assert response.status_code == HTTPStatus.NOT_IMPLEMENTED
