import os

from product.models.products.product import ProductChangeNotification
from product.stream_processor.integrations.events.event_handler import ProductChangeNotificationHandler
from product.stream_processor.integrations.events.models.output import EventReceipt
from product.stream_processor.integrations.events.providers.eventbridge import EventBridge

# NOTE: these will move to environment variables. Event source format could even use a pydantic validation!
EVENT_BUS = os.environ.get('EVENT_BUS', '')
EVENT_SOURCE = 'myorg.product.product_notification'


def notify_product_updates(update: list[ProductChangeNotification], event_handler: ProductChangeNotificationHandler | None = None) -> EventReceipt:
    """Notify product change notifications using default or provided event handler.

    Parameters
    ----------
    update : list[ProductChangeNotification]
        List of product change notifications to notify.
    event_handler : ProductChangeNotificationHandler | None, optional
        Event handler to use for notification, by default ProductChangeNotificationHandler

    Environment variables
    ---------------------
    `EVENT_BUS` : Event Bus to notify product change notifications

    # Examples

    Sending a newly added product notification

    ```python
    from product.stream_processor.domain_logic.product_notification import notify_product_updates

    notification = ProductChangeNotification(product_id=product_id, status="ADDED")
    receipt = notify_product_updates(update=[notification])
    ```

    Integrations
    ------------

    # Events

    * `ProductChangeNotificationHandler` uses `EventBridge` provider to convert and publish `ProductChangeNotification` models into events.

    Returns
    -------
    EventReceipt
        Receipts for unsuccessfully and successfully published events.
    """
    if event_handler is None:
        event_handler = ProductChangeNotificationHandler(provider=EventBridge(EVENT_BUS), event_source=EVENT_SOURCE)

    return event_handler.emit(payload=update)
