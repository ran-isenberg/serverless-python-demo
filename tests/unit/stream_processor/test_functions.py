from pydantic import BaseModel

from product.stream_processor.dal.events.functions import build_events_from_models, chunk_from_list, convert_model_to_event_name
from product.stream_processor.dal.events.models.input import Event


def test_chunk_from_list_returns_empty_list_when_list_is_empty():
    # GIVEN an empty list of items and a chunk size of 3
    list_of_items = []
    chunk_size = 3
    expected_chunk = []

    # WHEN we call chunk_from_list
    actual_chunk = chunk_from_list(list_of_items, chunk_size)

    # THEN we get an empty chunk
    assert list(actual_chunk) == expected_chunk


def test_chunk_from_list_returns_single_chunk_when_list_size_is_less_than_chunk_size():
    # GIVEN a list of items and a chunk size of 3
    list_of_items = [1, 2, 3]
    chunk_size = 3
    expected_chunk = [1, 2, 3]

    # WHEN we call chunk_from_list
    actual_chunk = next(chunk_from_list(list_of_items, chunk_size))

    # THEN we get a chunk of the same size as the list
    assert actual_chunk == expected_chunk
    assert len(actual_chunk) == len(expected_chunk)
    assert len(actual_chunk) == len(list_of_items)


def test_chunk_from_list_returns_multiple_chunks_when_list_size_is_greater_than_chunk_size():
    # GIVEN a list of items and a chunk size of 3
    list_of_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chunk_size = 3
    expected_chunks = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

    # WHEN we call chunk_from_list
    actual_chunks = list(chunk_from_list(list_of_items, chunk_size))

    # THEN we get a chunk of the same size as the list
    assert actual_chunks == expected_chunks


def test_convert_pascal_case_to_snake_case_with_convert_model_to_event_name():
    # GIVEN a model name in pascal case
    model_name = 'ProductNotification'

    # WHEN we call convert_model_to_event_name
    event_name = convert_model_to_event_name(model_name)

    # THEN we get the expected event name
    assert event_name == 'product_notification'.upper()


def test_convert_model_to_event_name_with_uppercase():
    # GIVEN a model name in pascal case
    model_name = 'ProductHTTPNotification'

    # WHEN we call convert_model_to_event_name
    event_name = convert_model_to_event_name(model_name)

    # THEN we get the expected event name
    assert event_name == 'product_http_notification'.upper()


def test_convert_model_to_event_name_with_numbers():
    # GIVEN a model name in pascal case
    model_name = 'ProductHTTPNotification123'

    # WHEN we call convert_model_to_event_name
    event_name = convert_model_to_event_name(model_name)

    # THEN we get the expected event name
    assert event_name == 'product_http_notification123'.upper()


def test_build_events_from_models():
    # GIVEN any Pydantic model
    class SampleNotification(BaseModel):
        message: str

    # WHEN we call build_events_from_models with all required fields
    notification = SampleNotification(message='Hello World!')
    event = build_events_from_models(models=[notification], event_source='sample')

    # THEN we get a list of Events
    assert type(event[0]) == Event
