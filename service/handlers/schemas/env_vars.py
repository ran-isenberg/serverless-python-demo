from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl


class Observability(BaseModel):
    POWERTOOLS_SERVICE_NAME: Annotated[str, Field(min_length=1)]
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']


class Idempotency(BaseModel):
    IDEMPOTENCY_TABLE_NAME: Annotated[str, Field(min_length=1)]


class MyHandlerEnvVars(Observability):
    REST_API: HttpUrl
    ROLE_ARN: Annotated[str, Field(min_length=20, max_length=2048)]
    TABLE_NAME: Annotated[str, Field(min_length=1)]
