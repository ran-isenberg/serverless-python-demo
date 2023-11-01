from pytest import FixtureRequest

from infrastructure.product.constants import STREAM_PROCESSOR_EVENT_SOURCE_NAME
from product.crud.integration import get_db_handler
from product.crud.models.product import Product
from tests.crud_utils import generate_product_id
from tests.data_fetcher.events import EventFetcher


def test_product_creation_leads_to_event(request: FixtureRequest, table_name: str, test_events_table: str):
    # GIVEN a single new product
    product = Product(id=generate_product_id(), name=request.node.name, price=10)

    # WHEN we create it in the database connected to the stream processor
    db_handler = get_db_handler(table_name)
    db_handler.create_product(product)

    # THEN we should have a single notification generated for a distinct product id
    events = EventFetcher(event_source=STREAM_PROCESSOR_EVENT_SOURCE_NAME, table_name=test_events_table)
    event_received = events.get_event_by_product_id(product.id)

    assert product.id in event_received.data
