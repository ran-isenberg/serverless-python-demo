import json
from http import HTTPStatus

import requests


def test_handler_bad_request_invalid_body(api_gw_url_slash_product: str, product_id: str):
    # when creating a product with invalid body payload,
    # and missing parameter name, get back HTTP BAD_REQUEST
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
