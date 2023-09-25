import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.schemas.input import GetPathParams


def test_invalid_product_id_invalid_string():
    with pytest.raises(ValidationError):
        GetPathParams.model_validate({'product': 'aa'})


def test_invalid_product_empty():
    with pytest.raises(ValidationError):
        GetPathParams.model_validate({})


def test_invalid_product_type_mismatch():
    with pytest.raises(ValidationError):
        GetPathParams.model_validate({'product': 6})


def test_invalid_json_key_but_valid_uuid(product_id):
    with pytest.raises(ValidationError):
        GetPathParams.model_validate({'order': product_id})


def test_valid_uuid_input(product_id):
    GetPathParams.model_validate({'product': product_id})
