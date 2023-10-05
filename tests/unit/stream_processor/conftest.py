from typing import Any, Sequence

from pytest_socket import disable_socket

from product.stream_processor.integrations.events.base import BaseEventHandler, BaseEventProvider
from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.integrations.events.models.input import AnyModel, Event
from product.stream_processor.integrations.events.models.output import EventReceipt, EventReceiptSuccess


def pytest_runtest_setup():
    """Disable Unix and TCP sockets for Data masking tests"""
    disable_socket()


# Fakes are in-memory implementations of our interface, serving the following purposes:
# -- Remove the need for mocks that need to be aware of scope and return types
# -- Make it easier to assert data structures that would be hard otherwise to introspect
# -- Simple reference for an EventHandler and EventProvider


class FakeProvider(BaseEventProvider):

    def send(self, payload: Sequence[Event]) -> EventReceipt:
        notifications = [EventReceiptSuccess(receipt_id='test') for _ in payload]
        return EventReceipt(success=notifications)


class FakeEventHandler(BaseEventHandler[AnyModel]):

    def __init__(self, event_source: str = 'fake', event_bus: str = 'fake_bus', provider: BaseEventProvider | None = None) -> None:
        self.provider = provider or FakeProvider()
        self.published_payloads: list[AnyModel] = []

        super().__init__(event_source=event_source, event_bus=event_bus, provider=self.provider)

    def emit(self, payload: list[AnyModel], metadata: dict[str, Any] | None = None, correlation_id='') -> EventReceipt:
        metadata = metadata or {}
        event_payload = EventHandler.build_events_from_models(models=payload, metadata=metadata, correlation_id=correlation_id, event_source='fake')
        receipt = self.provider.send(payload=event_payload)

        self.published_payloads.extend(payload)
        return receipt

    def __len__(self):
        return len(self.published_payloads)

    def __contains__(self, item: AnyModel):
        return item in self.published_payloads
