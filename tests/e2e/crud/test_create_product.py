import json
from http import HTTPStatus

import requests

from tests.crud_utils import generate_create_product_request_body


def test_handler_200_ok(api_gw_url_slash_product: str, product_id: str):
    # when creating a product, the returned response is the correct product id we sent as input
    body = generate_create_product_request_body()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id

    # check idempotency, send same request, get bad request as it already exists
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict['error'] == 'product already exists'


def test_handler_bad_request_invalid_body(api_gw_url_slash_product: str, product_id: str):
    # when creating a product with invalid boy payload, missing parameter name, get back HTTP BAD_REQUEST
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
