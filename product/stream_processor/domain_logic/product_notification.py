import os

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.event_handler import ProductNotificationHandler
from product.stream_processor.dal.events.providers.eventbridge import EventBridge

EVENT_BUS = os.environ.get('EVENT_BUS', '')


def notify_product_updates(update: list[ProductNotification], event_handler: ProductNotificationHandler | None = None):
    if event_handler is None:
        event_handler = ProductNotificationHandler(provider=EventBridge(EVENT_BUS))

    return event_handler.emit(payload=update)
