import pytest

from product.models.products.validators import validate_product_id


# Invalid ids
@pytest.mark.parametrize(
    'invalid_id',
    [
        'aaaa',  # non-uuid string
        '12345678-1234-1234-1234-1234567890zz',  # uuid with invalid characters
        '',  # empty string
        None,  # None value
        123,  # integer
        12.3,  # float
    ],
)
def test_invalid_id(invalid_id):
    # GIVEN an invalid id
    # WHEN attempting to validate it using validate_product_id
    # THEN a ValueError should be raised
    with pytest.raises(ValueError):
        validate_product_id(invalid_id)


def test_valid_id(product_id):
    # GIVEN a valid id
    # WHEN attempting to validate it using validate_product_id
    # THEN it should be validated without errors
    validate_product_id(product_id)
