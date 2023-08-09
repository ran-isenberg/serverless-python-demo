import json
from http import HTTPStatus

import pytest
import requests

from cdk.service.constants import APIGATEWAY, GW_RESOURCE
from tests.crud_utils import generate_create_product_request_body, generate_product_id
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api/{GW_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()


def test_handler_200_ok(api_gw_url: str, product_id: str):
    body = generate_create_product_request_body()
    url_with_product_id = f'{api_gw_url}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == body.id

    # check idempotency, send same request
    response = requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10)
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == body.id


def test_handler_bad_request(api_gw_url: str, product_id: str):
    body_str = json.dumps({'price': 5})
    url_with_product_id = f'{api_gw_url}/{product_id}'
    response = requests.put(url=url_with_product_id, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
