from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Observability(BaseModel):
    POWERTOOLS_SERVICE_NAME: Annotated[str, Field(min_length=1)]
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']


class Idempotency(BaseModel):
    IDEMPOTENCY_TABLE_NAME: Annotated[str, Field(min_length=1)]


class CreateVars(Observability, Idempotency):
    TABLE_NAME: Annotated[str, Field(min_length=1)]


class GetVars(Observability):
    TABLE_NAME: Annotated[str, Field(min_length=1)]
