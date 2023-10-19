from product.stream_processor.integrations.events.base import BaseEventHandler
from product.stream_processor.integrations.events.models.output import EventReceipt
from product.stream_processor.models.product import ProductChangeNotification


def notify_product_updates(update: list[ProductChangeNotification], event_handler: BaseEventHandler) -> EventReceipt:
    """Notify product change notifications using default or provided event handler.

    Parameters
    ----------
    update : list[ProductChangeNotification]
        List of product change notifications to notify.
    event_handler : BaseEventHandler
        Event handler to use for notification

    Environment variables
    ---------------------
    `EVENT_BUS` : Event Bus to notify product change notifications

    # Examples

    Sending a newly added product notification

    ```python
    from product.stream_processor.domain_logic.product_notification import notify_product_updates


    notification = ProductChangeNotification(product_id=product_id, status="ADDED")
    event_handler =
    receipt = notify_product_updates(update=[notification])
    ```

    Integrations
    ------------

    # Events

    * `EventHandler` uses `EventBridge` provider to convert and publish `ProductChangeNotification` models into events.
    * `EventHandler` uses `EventBridge` provider to convert and publish `ProductChangeNotification` models into events.

    Returns
    -------
    EventReceipt
        Receipts for unsuccessfully and successfully published events.
    """
    return event_handler.emit(payload=update)
