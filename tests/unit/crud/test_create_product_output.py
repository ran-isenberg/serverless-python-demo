import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from service.crud.schemas.output import CreateProductOutput


def test_invalid_product_id():
    with pytest.raises(ValidationError):
        CreateProductOutput(id='2', customer_name='3333', order_item_count=2)


def test_valid_output(product_id):
    CreateProductOutput(name='222', price=4, id=product_id)
