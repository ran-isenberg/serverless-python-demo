from product.stream_processor.domain_logic.product_notification import notify_product_updates
from tests.unit.stream_processor.conftest import FakeEventHandler
from tests.unit.stream_processor.data_builder import generate_product_notifications


def test_product_notifications_are_emitted():
    # GIVEN a list of Product Notifications and a fake event handler
    product_notifications = generate_product_notifications()
    event_store = FakeEventHandler()

    # WHEN the product notifications are processed
    receipt = notify_product_updates(update=product_notifications, event_handler=event_store)

    # THEN the fake event handler should emit these product notifications
    assert len(receipt.successful_notifications) == len(product_notifications)
    assert all(notification in event_store for notification in product_notifications)
