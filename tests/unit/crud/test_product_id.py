from service.crud.schemas.shared_types import validate_uuid
import pytest


def test_invalid_id():
    with pytest.raises(ValueError):
        validate_uuid('aaaa')


def test_valid_id(product_id):
    validate_uuid(product_id)
