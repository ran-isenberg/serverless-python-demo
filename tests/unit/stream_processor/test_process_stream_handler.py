from product.stream_processor.handlers.process_stream import process_stream
from tests.unit.stream_processor.conftest import FakeEventHandler
from tests.utils import generate_context


def test_process_stream_notify_product_updates(dynamodb_stream_events: dict, event_store: FakeEventHandler):
    # GIVEN a DynamoDB stream event and a fake event handler
    # WHEN process_stream is called with a custom event handler
    process_stream(event=dynamodb_stream_events, context=generate_context(), event_handler=event_store)

    # THEN the fake event handler should emit these product notifications
    # and no errors should have been raised (e.g., no sockets, no DAL calls)
    assert len(dynamodb_stream_events['Records']) == len(event_store)


# NOTE: this should fail once we have schema validation
def test_process_stream_with_empty_records(event_store: FakeEventHandler):
    # GIVEN an empty DynamoDB stream event
    event: dict[str, list] = {'Records': []}

    # WHEN process_stream is called with a custom event handler
    process_stream(event=event, context=generate_context(), event_handler=event_store)

    # THEN the fake event handler should emit these product notifications
    # and no errors should have been raised
    assert len(event_store) == 0
