import os

from product.models.products.product import ProductChangeNotification
from product.stream_processor.integrations.events.event_handler import ProductChangeNotificationHandler
from product.stream_processor.integrations.events.providers.eventbridge import EventBridge

EVENT_BUS = os.environ.get('EVENT_BUS', '')
EVENT_SOURCE = 'myorg.product.product_notification'


def notify_product_updates(update: list[ProductChangeNotification], event_handler: ProductChangeNotificationHandler | None = None):
    if event_handler is None:
        event_handler = ProductChangeNotificationHandler(provider=EventBridge(EVENT_BUS), event_source=EVENT_SOURCE)

    return event_handler.emit(payload=update)
