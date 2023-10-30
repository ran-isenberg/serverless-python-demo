from http import HTTPStatus

import requests

from product.crud.models.output import ListProductsOutput
from product.crud.models.product import Product
from tests.e2e.crud.utils import get_auth_header


# create product and then get it back
def test_handler_200_ok(api_gw_url_slash_products: str, add_product_entry_to_db: Product, id_token: str) -> None:
    # when starting with an empty table, creating a new product and then listing products will return a list with one product - the one we created
    response: requests.Response = requests.get(url=api_gw_url_slash_products, timeout=10, headers=get_auth_header(id_token))

    # assert response
    assert response.status_code == HTTPStatus.OK
    response_entry = ListProductsOutput.model_validate_json(response.text)
    products = response_entry.products
    # we cleared the table so only one product
    assert len(products) == 1
    # assert we got the item we expect
    assert products[0].model_dump() == add_product_entry_to_db.model_dump()


def test_handler_invalid_path(api_gw_url: str, id_token: str) -> None:
    # when calling GET on invalid path (not /products), get HTTP FORBIDDEN
    url_with_product_id = f'{api_gw_url}/dummy'
    response = requests.get(url=url_with_product_id, headers=get_auth_header(id_token))
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_handler_invalid_auth(api_gw_url_slash_products: str, id_token: str) -> None:
    # when calling GET on /products with invalid id token, get HTTP UNAUTHORIZED
    response = requests.get(url=api_gw_url_slash_products, headers=get_auth_header('aaaa'))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
