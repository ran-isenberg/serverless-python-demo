from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt

T = TypeVar('T')

# negative look ahead (?|char). Don't try to match the start of the string and any underscore that follows e.g., `_<name>` and `__<name>`

# full regex: ((?!^)(?<!_)[A-Z][a-z]+|(?<=[a-z0-9])[A-Z])
# ProductNotification -> Product_Notification
# ProductNotificationV2 -> Product_Notification_V2
# ProductHTTP -> Product_HTTP


class EventProvider(ABC):

    @abstractmethod
    def send(self, payload: list[Event]) -> EventReceipt:
        ...


class EventHandler(ABC, Generic[T]):

    def __init__(self, provider: EventProvider, event_source: str) -> None:
        self.provider = provider
        self.event_source = event_source

    @abstractmethod
    def emit(self, payload: list[T], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        ...
