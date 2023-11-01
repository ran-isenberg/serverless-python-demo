import requests

from infrastructure.product.constants import STREAM_PROCESSOR_EVENT_SOURCE_NAME
from tests.crud_utils import generate_create_product_request_body
from tests.data_fetcher.events import EventFetcher
from tests.e2e.crud.utils import get_auth_header


def test_create_product_stream_processing(test_events_table: str, api_gw_url_slash_product: str, product_id: str, id_token: str):
    # GIVEN a URL and product ID for creating a product
    body = generate_create_product_request_body()
    url_with_product_id = f'{api_gw_url_slash_product}/{product_id}'

    # WHEN making a PUT request to create a product
    requests.put(url=url_with_product_id, data=body.model_dump_json(), timeout=10, headers=get_auth_header(id_token))

    # THEN we should have a single notification generated for the newly created product
    events = EventFetcher(event_source=STREAM_PROCESSOR_EVENT_SOURCE_NAME, table_name=test_events_table)
    event_received = events.get_event_by_product_id(product_id)

    assert product_id in event_received.data
