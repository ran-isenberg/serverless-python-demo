from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt

T = TypeVar('T')


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
