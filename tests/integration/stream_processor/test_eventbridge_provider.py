from _pytest.fixtures import FixtureRequest
from pydantic import BaseModel

from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.integrations.events.providers.eventbridge import EventBridge
from tests.data_fetcher.events import EventFetcher


def test_eventbridge_provider_send(request: FixtureRequest, event_bus: str, test_events_table: str):
    # GIVEN an event bus, event source named after this test name, a notification
    class SampleNotification(BaseModel):
        message: str

    notification = SampleNotification(message='test')
    event_source = request.node.name  # test name
    event_provider = EventBridge(bus_name=event_bus)

    # WHEN EventBridge provider sends an event
    events = EventHandler.build_events_from_models(models=[notification], event_source=event_source)
    receipt = event_provider.send(payload=events)

    # THEN EventBridge should deliver this event to anyone listening
    receipt_id = receipt.success[0].receipt_id

    fetcher = EventFetcher(event_source=event_source, table_name=test_events_table)
    event_received = fetcher.get_event(receipt_id)

    assert event_received.receipt_id == receipt_id
    assert event_received.metadata == events[0].metadata.model_dump_json()
    assert event_received.data == events[0].data.model_dump_json()
