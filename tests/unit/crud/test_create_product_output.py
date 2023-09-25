import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.schemas.output import CreateProductOutput


def test_invalid_product_id():
    with pytest.raises(ValidationError):
        CreateProductOutput(id='2')


def test_valid_output(product_id):
    CreateProductOutput(id=product_id)
