from tests.utils import generate_product_id

import pytest


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()
