from datetime import datetime

from aws_lambda_powertools import Logger
from pydantic import BaseModel, Field

logger = Logger()


class EventMetadata(BaseModel):
    event_name: str
    event_source: str
    event_version: str
    correlation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(BaseModel):
    data: BaseModel
    metadata: EventMetadata
