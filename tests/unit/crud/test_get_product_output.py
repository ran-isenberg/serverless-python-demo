import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.schemas.output import GetProductOutput


def test_invalid_product_id():
    with pytest.raises(ValidationError):
        GetProductOutput(id='2')


def test_valid_output(product_id):
    GetProductOutput(id=product_id, name='3333', price=5)


def test_invalid_items_price(product_id):
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='3333', price='a')


def test_invalid_price_negative(product_id):
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='3333', price=-1)


def test_invalid_price_zero(product_id):
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='3333', price=0)


def test_invalid_long_name(product_id):
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='33333333333333333333333', price=1)


def test_invalid_empty_name(product_id):
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='', price=1)
