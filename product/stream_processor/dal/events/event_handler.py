from typing import Any
from uuid import uuid4

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.base import EventHandler, EventProvider
from product.stream_processor.dal.events.models.output import EventReceipt
from product.stream_processor.dal.events.models.input import Event, EventMetadata


class ProductNotificationHandler(EventHandler):
    EVENT_SOURCE = 'myorg.product.product_notification'

    def __init__(self, provider: EventProvider) -> None:
        self.provider = provider

    def emit(self, payload: list[ProductNotification], metadata: dict[str, Any] | None = None) -> EventReceipt:
        metadata = metadata or {}
        correlation_id = f'{uuid4()}'  # we want the same correlation ID for the batch

        event_payload = [
            Event(
                data=notification.to_dict(),
                metadata=EventMetadata(
                    event_type=notification.event_name,
                    event_source=self.EVENT_SOURCE,
                    event_version=notification.event_version,
                    correlation_id=correlation_id,
                )
            )
            for notification in payload
        ]

        return self.provider.send(event_payload)
