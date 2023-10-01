from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T')
R = TypeVar('R')


class EventProvider(ABC, Generic[T, R]):

    @abstractmethod
    def send(self, payload: T) -> R:
        ...


class EventHandler(ABC, Generic[T, R]):

    def __init__(self, emitter: EventProvider) -> None:
        ...

    @abstractmethod
    def emit(self, payload: list[T], metadata: dict[str, Any] | None = None) -> R:
        ...
