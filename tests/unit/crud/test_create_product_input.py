import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.models.input import CreateProductBody


def test_invalid_name():
    # GIVEN an invalid name (empty string)
    # WHEN creating a product input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductBody(name='', price=4)


def test_invalid_name_too_long():
    # GIVEN an invalid name (length > max allowed length)
    # WHEN creating a product input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductBody(name='1234567890112123423232323232323', price=4)


def test_missing_mandatory_fields():
    # GIVEN a missing mandatory field (price)
    # WHEN creating a product input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductBody(name='a')


def test_invalid_price():
    # GIVEN an invalid price (negative value)
    # WHEN creating a product input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductBody(name='a', price=-1)


def test_invalid_price_type():
    # GIVEN an invalid price (non-numeric value)
    # WHEN creating a product input
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductBody(name='a', price='a')


def test_valid_input():
    # GIVEN valid input data (name and price)
    # WHEN creating a product input
    # THEN no error should be raised and the instance should be created successfully
    CreateProductBody(name='a', price=4)
