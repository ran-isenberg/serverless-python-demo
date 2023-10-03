import re
from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar
from uuid import uuid4

from product.stream_processor.dal.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.dal.events.models.input import AnyModel, Event, EventMetadata
from product.stream_processor.dal.events.models.output import EventReceipt

T = TypeVar('T')

# negative look ahead (?|char). Don't try to match the start of the string and any underscore that follows e.g., `_<name>` and `__<name>`
_exclude_underscores = r'(?!^)(?<!_)'

_pascal_case = r'[A-Z][a-z]+'
_followed_by_lower_case_or_digit = r'(?<=[a-z0-9])[A-Z])'  # V1ProductNotification
_or = r'|'

# full regex: ((?!^)(?<!_)[A-Z][a-z]+|(?<=[a-z0-9])[A-Z])
# ProductNotification -> Product_Notification
# ProductNotificationV2 -> Product_Notification_V2
# ProductHTTP -> Product_HTTP
_pascal_to_snake_pattern = re.compile(rf'({_exclude_underscores}{_pascal_case}{_or}{_followed_by_lower_case_or_digit}')


class EventProvider(ABC):

    @abstractmethod
    def send(self, payload: Sequence[Event]) -> EventReceipt:
        ...


class EventHandler(ABC, Generic[T]):

    def __init__(self, provider: EventProvider, event_source: str) -> None:
        self.provider = provider
        self.event_source = event_source

    @abstractmethod
    def emit(self, payload: Sequence[T], metadata: dict[str, Any] | None = None) -> EventReceipt:
        ...


def convert_model_to_event_name(model_name: str) -> str:
    """ Convert ModelName (pascal) to MODEL_NAME (snake, uppercase)"""
    return _pascal_to_snake_pattern.sub(r'_\1', model_name).upper()


def build_events_from_models(models: Sequence[AnyModel], event_source: str, metadata: dict[str, Any] | None = None,
                             correlation_id: str = '') -> list[Event]:
    metadata = metadata or {}
    correlation_id = correlation_id or f'{uuid4()}'

    events = []

    for model in models:
        event_name = convert_model_to_event_name(model_name=model.__class__.__name__)
        event_version = getattr(model, '__version__', DEFAULT_EVENT_VERSION)  # defaults to v1

        events.append(
            Event(
                data=model, metadata=EventMetadata(event_name=event_name, event_source=event_source, event_version=event_version,
                                                   correlation_id=correlation_id, **metadata)))

    return events
