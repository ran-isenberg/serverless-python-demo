from product.models.products.product import ProductChangeNotification
from product.stream_processor.domain_logic.product_notification import notify_product_updates
from tests.unit.stream_processor.conftest import FakeEventHandler


def test_product_notifications_are_emitted(product_notifications: list[ProductChangeNotification], event_store: FakeEventHandler):
    # GIVEN a list of Product Notifications and a fake event handler
    # WHEN the product notifications are processed
    notify_product_updates(update=product_notifications, event_handler=event_store)

    # THEN the fake event handler should emit these product notifications
    assert len(event_store) == len(product_notifications)
    assert all(notification in event_store for notification in product_notifications)
