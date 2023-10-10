import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.schemas.input import CreateProductBody


def test_invalid_name():
    with pytest.raises(ValidationError):
        CreateProductBody(
            name='',
            price=4,
        )


def test_missing_mandatory_fields():
    with pytest.raises(ValidationError):
        CreateProductBody(name='a')
