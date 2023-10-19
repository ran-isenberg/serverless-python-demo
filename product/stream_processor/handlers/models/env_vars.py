from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Observability(BaseModel):
    POWERTOOLS_SERVICE_NAME: Annotated[str, Field(min_length=1)]
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'EXCEPTION']


class PrcStreamVars(Observability):
    EVENT_BUS: Annotated[str, Field(min_length=1)]
    EVENT_SOURCE: Annotated[str, Field(min_length=1)]
