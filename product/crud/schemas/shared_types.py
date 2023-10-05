from typing import Annotated
from uuid import UUID

from pydantic import Field
from pydantic.functional_validators import AfterValidator


def validate_uuid(v: str) -> str:
    try:
        UUID(v, version=4)
    except Exception as exc:
        raise ValueError(str(exc))
    return v


ProductId = Annotated[str, Field(min_length=36, max_length=36), AfterValidator(validate_uuid)]
