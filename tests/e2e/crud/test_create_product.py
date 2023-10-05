import json
from http import HTTPStatus

import requests

from tests.crud_utils import generate_create_product_request_body


def test_handler_200_ok(api_gw_url_slash_product: str, product_id: str):
    # GIVEN a URL and product ID for creating a product
    # AND a valid request body for creating a product
    body = generate_create_product_request_body()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'

    # WHEN making a PUT request to create a product
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)

    # THEN the response should indicate success (HTTP 200)
    # AND the response body should contain the provided product ID
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id

    # AND WHEN making the same PUT request again
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)

    # THEN the response should indicate a bad request (HTTP 400)
    # AND the response body should indicate the error due to product existence
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict['error'] == 'product already exists'


def test_handler_bad_request_invalid_body(api_gw_url_slash_product: str, product_id: str):
    # GIVEN a URL and product ID for creating a product
    # AND an invalid request body missing the "name" parameter
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'

    # WHEN making a PUT request to create a product with the invalid body
    response = requests.put(url=url_with_product_id, data=body_str, timeout=10)

    # THEN the response should indicate a bad request (HTTP 400)
    assert response.status_code == HTTPStatus.BAD_REQUEST
