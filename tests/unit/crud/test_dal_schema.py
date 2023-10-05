import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.integration.schemas.db import Product


def test_invalid_items_price(product_id):
    # GIVEN an invalid price type
    # WHEN creating a product
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price='a')


def test_invalid_price_negative(product_id):
    # GIVEN a negative price
    # WHEN creating a product
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price=-1)


def test_invalid_price_zero(product_id):
    # GIVEN a zero price
    # WHEN creating a product
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        Product(id=product_id, name='3333', price=0)


def test_invalid_product_id():
    # GIVEN an invalid product id (does not meet format/requirements)
    # WHEN creating a product
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        Product(id='2', name='3333', price=2)


def test_valid_output(product_id):
    # GIVEN valid input data
    # WHEN creating a product
    # THEN no error should be raised and the instance should be created successfully
    Product(name='222', price=4, id=product_id)
