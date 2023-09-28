import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.dal.schemas.db import Product


def test_invalid_items_price(product_id):
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price='a')


def test_invalid_price_negative(product_id):
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price=-1)


def test_invalid_price_zero(product_id):
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price=0)


def test_invalid_product_id():
    with pytest.raises(ValidationError):
        Product(id='2', name='3333', price=2)


def test_valid_output(product_id):
    Product(name='222', price=4, id=product_id)
