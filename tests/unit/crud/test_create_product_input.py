import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.crud.schemas.input import CreateProductRequest


def test_invalid_name(product_id):
    with pytest.raises(ValidationError):
        CreateProductRequest(id=product_id, name='', price=4)


def test_invalid_name_too_long(product_id):
    with pytest.raises(ValidationError):
        CreateProductRequest(id=product_id, name='1234567890112123423232323232323', price=4)


def test_missing_mandatory_fields(product_id):
    with pytest.raises(ValidationError):
        CreateProductRequest(id=product_id, name='a')


def test_invalid_price(product_id):
    with pytest.raises(ValidationError):
        CreateProductRequest(id=product_id, name='a', price=-1)


def test_invalid_price_type(product_id):
    with pytest.raises(ValidationError):
        CreateProductRequest(id=product_id, name='a', price='a')


def test_valid_input(product_id):
    CreateProductRequest(id=product_id, name='a', price=4)


def test_invalid_id():
    with pytest.raises(ValidationError):
        CreateProductRequest(id='aaa', name='a', price=4)
