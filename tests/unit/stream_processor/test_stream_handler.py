from tests.unit.stream_processor.data_builder import generate_dynamodb_stream_events
from product.stream_processor.handlers.stream_handler import process_stream
from tests.utils import generate_context
import uuid


def test_process_stream_notify_product_updates():
    # GIVEN
    product_id = f'{uuid.uuid4()}'
    events = generate_dynamodb_stream_events(product_id=product_id)

    # WHEN
    ret = process_stream(events, generate_context())

    # THEN
    assert all(product.product_id == product_id for product in ret)
