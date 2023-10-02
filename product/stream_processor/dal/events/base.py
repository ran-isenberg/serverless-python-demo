from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from product.stream_processor.dal.events.models.output import EventReceipt

T = TypeVar('T')
R = TypeVar('R')


class EventProvider(ABC, Generic[T, R]):

    @abstractmethod
    def send(self, payload: T) -> R:
        ...


class EventHandler(ABC, Generic[T, R]):

    def __init__(self, provider: EventProvider) -> None:
        ...

    @abstractmethod
    def emit(self, payload: list[T], metadata: dict[str, Any] | None = None) -> EventReceipt:
        ...
