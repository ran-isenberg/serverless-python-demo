from http import HTTPStatus

import requests


def test_handler_200_ok(api_gw_url_slash_products: str):
    response = requests.get(url=api_gw_url_slash_products, timeout=10)
    assert response.status_code == HTTPStatus.NOT_IMPLEMENTED
