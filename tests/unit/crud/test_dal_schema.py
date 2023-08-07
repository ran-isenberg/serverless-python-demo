import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.crud.dal.schemas.db import ProductEntry


def test_invalid_items_type(product_id):
    with pytest.raises(ValidationError):
        ProductEntry(id=product_id, name='3333', price='a')


def test_invalid_items_negative(product_id):
    with pytest.raises(ValidationError):
        ProductEntry(id=product_id, name='3333', price=-1)


def test_invalid_items_zero(product_id):
    with pytest.raises(ValidationError):
        ProductEntry(id=product_id, name='3333', price=0)


def test_invalid_product_id():
    with pytest.raises(ValidationError):
        ProductEntry(id='2', name='3333', price=2)


def test_valid_output(product_id):
    ProductEntry(name='222', price=4, id=product_id)
