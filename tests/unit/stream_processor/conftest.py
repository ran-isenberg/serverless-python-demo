from typing import Any, Generator, TypeVar

import pytest

from product.models.products.product import ProductNotification
from product.stream_processor.dal.events.event_handler import ProductNotificationHandler
from tests.unit.stream_processor.data_builder import generate_dynamodb_stream_events, generate_product_notifications

T = TypeVar('T')
Fixture = Generator[T, None, None]


class FakeEventHandler(ProductNotificationHandler):

    def __init__(self):
        self.published_events = []

    def emit(self, payload: list[ProductNotification], metadata: dict[str, Any] | None = None):
        metadata = metadata or {}
        for product in payload:
            self.published_events.append({'event': product, 'metadata': metadata})

    def __len__(self):
        return len(self.published_events)


@pytest.fixture
def dynamodb_stream_events() -> Fixture[dict[str, Any]]:
    yield generate_dynamodb_stream_events()


@pytest.fixture
def event_store() -> Fixture[FakeEventHandler]:
    yield FakeEventHandler()
