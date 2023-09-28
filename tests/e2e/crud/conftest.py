from typing import Generator

import pytest

from infrastructure.product.constants import APIGATEWAY, PRODUCT_RESOURCE, PRODUCTS_RESOURCE, TABLE_NAME_OUTPUT
from product.crud.dal.schemas.db import Product
from tests.crud_utils import clear_table, generate_product_id
from tests.e2e.crud.utils import create_product, delete_product
from tests.utils import get_stack_output


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_product():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCT_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def api_gw_url_slash_products():
    return f'{get_stack_output(APIGATEWAY)}api/{PRODUCTS_RESOURCE}'


@pytest.fixture(scope='module', autouse=True)
def api_gw_url():
    return f'{get_stack_output(APIGATEWAY)}api'


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()


@pytest.fixture(scope='module', autouse=True)
def table_name():
    return get_stack_output(TABLE_NAME_OUTPUT)


@pytest.fixture()
def add_product_entry_to_db(api_gw_url_slash_product: str, table_name: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product_id = generate_product_id()
    product = Product(id=product_id, price=1, name='test')
    create_product(api_gw_url_slash_product=api_gw_url_slash_product, product_id=product_id, price=product.price, name=product.name)
    yield product
    delete_product(api_gw_url_slash_product, product_id)
