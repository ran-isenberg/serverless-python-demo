from datetime import datetime
from typing import TypeVar

from aws_lambda_powertools import Logger
from pydantic import BaseModel, ConfigDict, Field

AnyModel = TypeVar('AnyModel', bound=BaseModel)
logger = Logger()


class EventMetadata(BaseModel):
    event_name: str
    event_source: str
    event_version: str
    correlation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra='allow')


class Event(BaseModel):
    data: AnyModel
    metadata: EventMetadata
