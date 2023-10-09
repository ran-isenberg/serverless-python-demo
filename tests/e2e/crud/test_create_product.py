import json
from http import HTTPStatus

import requests

from tests.crud_utils import generate_create_product_request_body, generate_product_id


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

    # THEN the response should indicate a 200 OK since idempotency is active within 1 minute range
    # AND the response body should contain the exact product id
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id

    # AND WHEN making a PUT request again with same product id but different price and name
    body = generate_create_product_request_body()
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)

    # THEN the response should indicate a bad request (HTTP 400)
    # AND the response body should indicate the error due to product existence (with different params)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict['error'] == 'product already exists'


def test_idempotency_does_not_affect_different_ids(api_gw_url_slash_product: str):
    # GIVEN a URL and product ID for creating a product
    # AND a valid request body for creating a product
    body = generate_create_product_request_body()
    expected_product_id = generate_product_id()
    url_with_product_id = f'{api_gw_url_slash_product}/{expected_product_id}'

    # WHEN making a PUT request to create a product
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)

    # THEN the response should indicate success (HTTP 200)
    # AND the response body should contain the provided product ID
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == expected_product_id

    # AND WHEN making a PUT request again with different product id
    body = generate_create_product_request_body()
    expected_product_id = generate_product_id()
    url_with_product_id = f'{api_gw_url_slash_product}/{expected_product_id}'
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)

    # THEN the response should indicate success (HTTP 200)
    # AND the response body should contain the new product ID
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == expected_product_id


def test_handler_bad_request_invalid_body(api_gw_url_slash_product: str, product_id: str):
    # GIVEN a URL and product ID for creating a product
    # AND an invalid request body missing the "name" parameter
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'

    # WHEN making a PUT request to create a product with the invalid body
    response = requests.put(url=url_with_product_id, data=body_str, timeout=10)

    # THEN the response should indicate a bad request (HTTP 400)
    assert response.status_code == HTTPStatus.BAD_REQUEST
