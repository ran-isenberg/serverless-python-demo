import pytest

from tests.utils import generate_product_id


@pytest.fixture(scope='module', autouse=True)
def product_id():
    return generate_product_id()
