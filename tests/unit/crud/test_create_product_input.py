import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.crud.schemas.input import PutProductBody


def test_invalid_name():
    with pytest.raises(ValidationError):
        PutProductBody(name='', price=4)


def test_invalid_name_too_long():
    with pytest.raises(ValidationError):
        PutProductBody(name='1234567890112123423232323232323', price=4)


def test_missing_mandatory_fields():
    with pytest.raises(ValidationError):
        PutProductBody(name='a')


def test_invalid_price():
    with pytest.raises(ValidationError):
        PutProductBody(name='a', price=-1)


def test_invalid_price_type():
    with pytest.raises(ValidationError):
        PutProductBody(name='a', price='a')


def test_valid_input():
    PutProductBody(name='a', price=4)
