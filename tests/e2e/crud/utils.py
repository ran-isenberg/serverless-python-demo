from http import HTTPStatus

import requests

from tests.crud_utils import generate_create_product_request_body


# create product and return its product id
def create_product(api_gw_url_slash_product: str, product_id: str, price: int, name: str, id_token: str) -> None:
    body = generate_create_product_request_body(price=price, name=name)

    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10, headers=get_auth_header(id_token))
    assert response.status_code == HTTPStatus.OK


# delete product by product id
def delete_product(api_gw_url_slash_product: str, product_id: str, id_token: str) -> None:
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.delete(url=url_with_product_id, timeout=10, headers=get_auth_header(id_token))
    assert response.status_code == HTTPStatus.NO_CONTENT


def get_auth_header(token: str):
    return {'Authorization': f'Bearer {token}'}
