from typing import TypeVar

from product.models.products.product import ProductNotification

# Until DAL gets created
EventHandler = TypeVar('EventHandler')


def notify_product_updates(
    update: list[ProductNotification], event_handler: EventHandler | None = None
):
    return update
