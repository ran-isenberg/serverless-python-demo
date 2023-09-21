import pytest

from infrastructure.product.constants import APIGATEWAY, PRODUCT_RESOURCE, PRODUCTS_RESOURCE
from tests.crud_utils import generate_product_id
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_product():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCT_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_products():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCTS_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()
