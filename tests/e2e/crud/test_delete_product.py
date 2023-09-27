from http import HTTPStatus

import requests

from tests.crud_utils import generate_product_id, generate_random_integer, generate_random_string
from tests.e2e.crud.utils import create_product


# create product and then delete it
def test_handler_200_ok(api_gw_url_slash_product: str) -> None:
    product_id = generate_product_id()
    price = generate_random_integer()
    name = generate_random_string()
    create_product(api_gw_url_slash_product=api_gw_url_slash_product, product_id=product_id, price=price, name=name)
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response: requests.Response = requests.delete(url=url_with_product_id, timeout=10)
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_handler_invalid_path(api_gw_url: str) -> None:
    url_with_product_id = f'{api_gw_url}/dummy'
    response = requests.delete(url=url_with_product_id)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_handler_invalid_product_id(api_gw_url_slash_product: str) -> None:
    url_with_product_id = f'{api_gw_url_slash_product}/aaaa'
    response = requests.delete(url=url_with_product_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
