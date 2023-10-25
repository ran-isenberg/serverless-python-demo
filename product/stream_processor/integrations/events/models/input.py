from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

AnyModel = TypeVar('AnyModel', bound=BaseModel)


class EventMetadata(BaseModel):
    """Data representation for a standard event metadata

    Parameters
    ----------
    event_name : str
        Name of the event, e.g., "PRODUCT_CHANGE_NOTIFICATION"
    event_source : str
        Event source, e.g., "myorg.service.feature"
    event_version : str
        Event version, e.g. "v1"
    correlation_id : str
        Correlation ID, e.g., "b76d27e1-bd2b-4aae-9781-1ef11063c5cd"

    created_at : datetime
        Timestamp of when the event was created (UTC)
    """

    event_name: str
    event_source: str
    event_version: str
    correlation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra='allow')


class Event(BaseModel, Generic[AnyModel]):
    """Data representation for a standard event

    Parameters
    ----------
    data : BaseModel
        Any Pydantic BaseModel
    metadata : EventMetadata
        Event metadata
    """

    data: AnyModel
    metadata: EventMetadata
