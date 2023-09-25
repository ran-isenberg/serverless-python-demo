import json
from http import HTTPStatus

import requests

from tests.crud_utils import generate_product_id


def test_handler_bad_request(api_gw_url: str) -> None:
    product_id = generate_product_id()
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
