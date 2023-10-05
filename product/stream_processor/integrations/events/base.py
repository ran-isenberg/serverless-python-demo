from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt

T = TypeVar('T')


class BaseEventProvider(ABC):
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


class BaseEventHandler(ABC, Generic[T]):

    def __init__(self, provider: BaseEventProvider, event_source: str) -> None:
        """ABC to handle event manipulation from a model, and publishing through a provider.

        Parameters
        ----------
        provider : BaseEventProvider
            Event Provider to publish events through.
        event_source : str
            Event source name, e.g., 'myorg.service.feature'
        """
        self.provider = provider
        self.event_source = event_source

    @abstractmethod
    def emit(self, payload: list[T], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        """Emits events using registered provider, along with additional metadata or specific correlation ID.

        Parameters
        ----------
        payload : list[T]
            List of models to convert and publish as an Event.
        metadata : dict[str, Any] | None, optional
            Additional metadata to be injected into the event before sending, by default None
        correlation_id : str, optional
            Correlation ID to inject in event metadata. We generate one if not provided.

        Returns
        -------
        EventReceipt
            Receipts for unsuccessfully and successfully published events.
        """
        ...
