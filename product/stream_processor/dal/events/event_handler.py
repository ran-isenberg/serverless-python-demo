from typing import Any

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.base import EventHandler, EventProvider


class ProductNotificationHandler(EventHandler):

    def __init__(self, provider: EventProvider) -> None:
        self.provider = provider

    def emit(self, payload: list[ProductNotification], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        metadata = metadata or {}
        return self.provider.send(payload)
