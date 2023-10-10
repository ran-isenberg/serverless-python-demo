import json
from http import HTTPStatus

import requests

from tests.crud_utils import generate_create_product_request_body


def test_handler_200_ok(api_gw_url_slash_product: str, product_id: str):
    body = generate_create_product_request_body()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'
    response = requests.put(
        url=url_with_product_id,
        data=body.model_dump_json(),
    )
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id
