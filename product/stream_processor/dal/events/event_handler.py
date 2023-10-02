from typing import Any
from uuid import uuid4

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.base import EventHandler, EventProvider
from product.stream_processor.dal.events.models.input import Event, EventMetadata
from product.stream_processor.dal.events.models.output import EventReceipt


class ProductNotificationHandler(EventHandler):

    def __init__(self, provider: EventProvider) -> None:
        self.provider = provider

    def emit(self, payload: list[ProductNotification], metadata: dict[str, Any] | None = None) -> EventReceipt:
        metadata = metadata or {}
        correlation_id = f'{uuid4()}'  # we want the same correlation ID for the batch; use logger correlation ID later

        # NOTE: this will be generic for all events later, we can easily make it reusable
        # also consider a method to build event from payload
        event_payload = [
            Event(
                data=notification.to_dict(),
                metadata=EventMetadata(event_type=notification.event_name, event_source=notification.event_source,
                                       event_version=notification.event_version, correlation_id=correlation_id, **metadata))
            for notification in payload
        ]

        return self.provider.send(payload=event_payload)
