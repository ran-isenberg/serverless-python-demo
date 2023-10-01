from typing import Any

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.base import EventHandler
from product.stream_processor.handlers.process_stream import process_stream
from tests.unit.stream_processor.data_builder import generate_dynamodb_stream_events
from tests.utils import generate_context


class FakeEventHandler(EventHandler):

    def __init__(self):
        self.published_events = []

    def emit(self, payload: list[ProductNotification], metadata: dict[str, Any] | None = None):
        metadata = metadata or {}
        for product in payload:
            self.published_events.append({'event': product, 'metadata': metadata})

    def __len__(self):
        return len(self.published_events)


def test_process_stream_notify_product_updates():
    # GIVEN a DynamoDB stream event and a fake event handler
    event = generate_dynamodb_stream_events()
    event_store = FakeEventHandler()

    # WHEN process_stream is called with a custom event handler
    process_stream(event=event, context=generate_context(), event_handler=event_store)

    # THEN the fake event handler should have received the correct number of events
    # and no errors should have been raised (e.g., no sockets, no DAL calls)
    assert len(event['Records']) == len(event_store)


# NOTE: this should fail once we have schema validation
def test_process_stream_with_empty_records():
    # GIVEN an empty DynamoDB stream event
    event = {'Records': []}
    event_store = FakeEventHandler()

    # WHEN process_stream is called with a custom event handler
    process_stream(event=event, context=generate_context(), event_handler=event_store)

    # THEN the fake event handler should have received no events
    # and no errors should have been raised
    assert len(event_store) == 0
