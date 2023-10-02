from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar

from product.stream_processor.dal.events.models.input import Event
from product.stream_processor.dal.events.models.output import EventReceipt

T = TypeVar('T')


class EventProvider(ABC):

    @abstractmethod
    def send(self, payload: Sequence[Event]) -> EventReceipt:
        ...


class EventHandler(ABC, Generic[T]):

    def __init__(self, provider: EventProvider) -> None:
        ...

    @abstractmethod
    def emit(self, payload: Sequence[T], metadata: dict[str, Any] | None = None) -> EventReceipt:
        ...
