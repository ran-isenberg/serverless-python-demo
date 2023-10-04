from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt

T = TypeVar('T')


class EventProvider(ABC):
    """ABC for an Event Provider that send events to a destination."""

    @abstractmethod
    def send(self, payload: list[Event]) -> EventReceipt:
        """Sends list of events to an Event Provider.

        Parameters
        ----------
        payload : list[Event]
            List of events to send.

        Returns
        -------
        EventReceipt
            Receipts for unsuccessfully and successfully published events.

        Raises
        ------
        NotificationDeliveryError
            When one or more events could not be delivered.
        """
        ...


class EventHandler(ABC, Generic[T]):

    def __init__(self, provider: EventProvider, event_source: str) -> None:
        self.provider = provider
        self.event_source = event_source

    @abstractmethod
    def emit(self, payload: list[T], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        ...
