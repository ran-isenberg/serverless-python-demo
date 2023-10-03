from typing import Any

from product.models.products.product import ProductChangeNotification
from product.stream_processor.dal.events.base import EventHandler, EventProvider, build_events_from_models
from product.stream_processor.dal.events.models.output import EventReceipt


class ProductChangeNotificationHandler(EventHandler):

    def __init__(self, provider: EventProvider, event_source: str) -> None:
        super().__init__(provider=provider, event_source=event_source)

    def emit(self, payload: list[ProductChangeNotification], metadata: dict[str, Any] | None = None, correlation_id: str = '') -> EventReceipt:
        event_payload = build_events_from_models(models=payload, metadata=metadata, correlation_id=correlation_id, event_source=self.event_source)
        return self.provider.send(payload=event_payload)
