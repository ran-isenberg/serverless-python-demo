import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.models.output import CreateProductOutput


def test_invalid_product_id():
    # GIVEN an invalid product id (does not meet format/requirements)
    # WHEN creating a product output
    # THEN a validation error should be raised
    with pytest.raises(ValidationError):
        CreateProductOutput(id='2')


def test_valid_output(product_id):
    # GIVEN a valid product id
    # WHEN creating a product output
    # THEN no error should be raised and the instance should be created successfully
    CreateProductOutput(id=product_id)
