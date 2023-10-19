import pytest
from aws_lambda_powertools.utilities.parser import ValidationError

from product.crud.models.input import ProductPathParams


@pytest.mark.parametrize(
    'invalid_input',
    [
        {
            'product': 'aa'
        },  # Invalid string
        {},  # Empty input
        {
            'product': 6
        },  # Type mismatch
        {
            'order': 'valid_uuid_here'
        }  # Invalid key, although UUID is valid
    ])
def test_invalid_input(invalid_input):
    with pytest.raises(ValidationError):
        ProductPathParams.model_validate(invalid_input)
