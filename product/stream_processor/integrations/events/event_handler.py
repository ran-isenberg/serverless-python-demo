from typing import Any

from product.models.products.product import ProductChangeNotification
from product.stream_processor.integrations.events.base import BaseEventHandler, BaseEventProvider
from product.stream_processor.integrations.events.models.output import EventReceipt


class ProductChangeNotificationHandler(BaseEventHandler):

    def __init__(self, provider: BaseEventProvider, event_source: str) -> None:
        """Event Handler for ProductChangeNotification.

        Parameters
        ----------
        provider : BaseEventProvider
            An event provider to send events to.
        event_source : str
            Event source to inject in event metadata, following 'myorg.service_name.feature_name'
        """
        super().__init__(provider=provider, event_source=event_source)

    def emit(self, payload: list[ProductChangeNotification], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        """Emits product change notifications using registered provider, along with additional metadata or specific correlation ID.

        Parameters
        ----------
        payload : list[ProductChangeNotification]
            List of product change notifications models to be sent.
        metadata : dict[str, Any] | None, optional
            Additional metadata to be injected into the event before sending, by default None
        correlation_id : str, optional
            Correlation ID to inject in event metadata. We generate one if not provided.

        Returns
        -------
        EventReceipt
            Receipts for unsuccessfully and successfully published events.
        """
        return super().emit(payload, metadata, correlation_id)
