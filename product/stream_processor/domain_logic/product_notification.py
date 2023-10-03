import os

from product.models.products.product import ProductChangeNotification
from product.stream_processor.dal.events.event_handler import ProductChangeNotificationHandler
from product.stream_processor.dal.events.providers.eventbridge import EventBridge

EVENT_BUS = os.environ.get('EVENT_BUS', '')


def notify_product_updates(update: list[ProductChangeNotification], event_handler: ProductChangeNotificationHandler | None = None):
    if event_handler is None:
        event_handler = ProductChangeNotificationHandler(provider=EventBridge(EVENT_BUS))

    return event_handler.emit(payload=update)
