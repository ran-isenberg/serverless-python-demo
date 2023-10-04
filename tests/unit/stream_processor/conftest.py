from typing import Any, Generator, Sequence, TypeVar

from pytest_socket import disable_socket

from product.models.products.product import ProductChangeNotification
from product.stream_processor.integrations.events.base import EventProvider
from product.stream_processor.integrations.events.event_handler import ProductChangeNotificationHandler
from product.stream_processor.integrations.events.functions import build_events_from_models
from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt, EventReceiptSuccess


def pytest_runtest_setup():
    """Disable Unix and TCP sockets for Data masking tests"""
    disable_socket()


T = TypeVar('T')
Fixture = Generator[T, None, None]

# Fakes are in-memory implementations of our interface, serving the following purposes:
# -- Remove the need for mocks that need to be aware of scope and return types
# -- Make it easier to assert data structures that would be hard otherwise to introspect
# -- Simple reference for an EventHandler and EventProvider


class FakeProvider(EventProvider):

    def send(self, payload: Sequence[Event]) -> EventReceipt:
        notifications = [EventReceiptSuccess(receipt_id='test') for _ in payload]
        return EventReceipt(success=notifications)


class FakeEventHandler(ProductChangeNotificationHandler):

    def __init__(self, provider: EventProvider = FakeProvider(), event_source: str = 'fake') -> None:
        super().__init__(provider=provider, event_source=event_source)
        self.published_payloads: list[ProductChangeNotification] = []

    def emit(self, payload: list[ProductChangeNotification], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        metadata = metadata or {}
        event_payload = build_events_from_models(models=payload, metadata=metadata, correlation_id=correlation_id, event_source='fake')
        receipt = self.provider.send(payload=event_payload)

        self.published_payloads.extend(payload)
        return receipt

    def __len__(self):
        return len(self.published_payloads)

    def __contains__(self, item: ProductChangeNotification):
        return item in self.published_payloads
