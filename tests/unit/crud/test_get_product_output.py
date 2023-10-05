import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.schemas.output import GetProductOutput


# Invalid product id
def test_invalid_product_id():
    # GIVEN an invalid product id, no UUID
    # WHEN attempting to create a GetProductOutput
    # THEN a ValidationError should be raised
    with pytest.raises(ValidationError):
        GetProductOutput(id='2', name='Name', price=5)


def test_valid_output(product_id):
    # GIVEN a valid product id, name, and price
    # WHEN attempting to create a GetProductOutput
    # THEN the object should be created without errors
    GetProductOutput(id=product_id, name='3333', price=5)


# Parameterize test function for several invalid prices
@pytest.mark.parametrize(
    'price',
    [
        'a',  # non-numeric price
        -1,  # negative price
        0,  # zero price
    ])
def test_invalid_price(product_id, price):
    # GIVEN an invalid price
    # WHEN attempting to create a GetProductOutput
    # THEN a ValidationError should be raised
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name='Name', price=price)


# Parameterize test function for several invalid names
@pytest.mark.parametrize(
    'name',
    [
        '',  # empty name
        'A' * 31,  # too long name assuming 30 is the limit
    ])
def test_invalid_name(product_id, name):
    # GIVEN an invalid name
    # WHEN attempting to create a GetProductOutput
    # THEN a ValidationError should be raised
    with pytest.raises(ValidationError):
        GetProductOutput(id=product_id, name=name, price=1)
