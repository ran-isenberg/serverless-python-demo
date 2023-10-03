from typing import Any, Generator, TypedDict, TypeVar

import pytest

from product.models.products.product import ProductChangeNotification
from product.stream_processor.dal.events.event_handler import ProductChangeNotificationHandler
from tests.unit.stream_processor.data_builder import generate_dynamodb_stream_events, generate_product_notifications
from pytest_socket import disable_socket


def pytest_runtest_setup():
    """Disable Unix and TCP sockets for Data masking tests"""
    disable_socket()


T = TypeVar('T')
Fixture = Generator[T, None, None]


class FakePublishedEvent(TypedDict):
    event: ProductChangeNotification
    metadata: dict[str, Any]


class FakeEventHandler(ProductChangeNotificationHandler):

    def __init__(self):
        self.published_events: list[FakePublishedEvent] = []

    def emit(self, payload: list[ProductChangeNotification], metadata: dict[str, Any] | None = None):
        metadata = metadata or {}
        for product in payload:
            self.published_events.append({'event': product, 'metadata': metadata})

    @property
    def published_notifications(self) -> list[ProductChangeNotification]:
        return [notification['event'] for notification in self.published_events]

    def __len__(self):
        return len(self.published_events)

    def __contains__(self, item: ProductChangeNotification):
        return item in self.published_notifications


@pytest.fixture
def dynamodb_stream_events() -> Fixture[dict[str, Any]]:
    yield generate_dynamodb_stream_events()


@pytest.fixture
def event_store() -> Fixture[FakeEventHandler]:
    yield FakeEventHandler()


@pytest.fixture
def product_notifications() -> Fixture[list[ProductChangeNotification]]:
    yield generate_product_notifications()
