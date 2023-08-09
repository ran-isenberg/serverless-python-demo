import json
from http import HTTPStatus

import pytest
import requests

from cdk.service.constants import APIGATEWAY, GW_RESOURCE
from service.crud.schemas.input import CreateProductRequest
from tests.utils import generate_product_id, generate_random_string, get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api/{GW_RESOURCE}'


def test_handler_200_ok(api_gw_url):
    product_name = generate_random_string()
    price = 5
    product_id = generate_product_id()
    body = CreateProductRequest(id=product_id, name=product_name, price=price)
    response = requests.post(api_gw_url, data=body.model_dump_json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id

    # check idempotency, send same request
    response = requests.post(api_gw_url, data=body.model_dump_json())
    assert response.status_code == HTTPStatus.OK
    body_dict = json.loads(response.text)
    assert body_dict['id'] == product_id


def test_handler_bad_request(api_gw_url):
    body_str = json.dumps({'price': 5})
    response = requests.post(api_gw_url, data=body_str)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    body_dict = json.loads(response.text)
    assert body_dict == {}
