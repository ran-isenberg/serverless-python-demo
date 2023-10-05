from uuid import uuid4

from pydantic import BaseModel

from product.stream_processor.integrations.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.integrations.events.models.input import Event


def test_model_to_standard_event():
    # GIVEN a model with __version__ set
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    notification = SampleNotification(message='testing')
    event_source = 'test'

    # WHEN we convert to an event
    event = EventHandler.build_events_from_models(models=[notification], event_source=event_source)[0]

    # THEN the event should contain our notification in `.data`, all metadata under `.metadata`
    # infer the event version from the model, event name infers model name from PascalCase to SNAKE_CASE_UPPER
    assert event.data == notification
    assert event.metadata.event_source == event_source
    assert event.metadata.event_version == notification.__version__
    assert event.metadata.event_name == EventHandler.extract_event_name_from_model(notification)
    assert event.metadata.correlation_id != ''
    assert event.metadata.created_at != ''


def test_model_to_standard_event_with_correlation_id():
    # GIVEN a model with __version__ set
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    notification = SampleNotification(message='testing')
    event_source = 'test'
    correlation_id = f'{uuid4()}'

    # WHEN we convert to an event
    event = EventHandler.build_events_from_models(models=[notification], event_source=event_source, correlation_id=correlation_id)[0]

    # THEN we should have the same correlation ID in the final event
    assert event.metadata.correlation_id == correlation_id


def test_model_to_standard_event_with_additional_metadata():
    # GIVEN a model with __version__ set
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    notification = SampleNotification(message='testing')
    event_source = 'test'
    metadata = {'product_id': 'test', 'username': 'lessa'}

    # WHEN we convert to an event
    event = EventHandler.build_events_from_models(models=[notification], event_source=event_source, metadata=metadata)[0]

    # THEN we should have additional metadata included in the final event
    assert metadata.items() <= event.metadata.model_dump().items()


def test_model_without_version_to_standard_event():
    # GIVEN a model without __version__ set
    class SampleNotification(BaseModel):
        message: str

    notification = SampleNotification(message='testing')
    event_source = 'test'

    # WHEN we convert to an event
    event = EventHandler.build_events_from_models(models=[notification], event_source=event_source)[0]

    # THEN we should add a default v1 version
    assert event.metadata.event_version == DEFAULT_EVENT_VERSION


def test_convert_pascal_case_to_snake_case_with_convert_model_to_event_name():
    # GIVEN a model name in pascal case
    class ProductNotification(BaseModel):
        message: str

    notification = ProductNotification(message='testing')

    # WHEN we call convert_model_to_event_name
    event_name = EventHandler.extract_event_name_from_model(notification)

    # THEN we get the expected event name
    assert event_name == 'product_notification'.upper()


def test_convert_model_to_event_name_with_uppercase():
    # GIVEN a model name in pascal case
    class ProductHTTPNotification(BaseModel):
        message: str

    notification = ProductHTTPNotification(message='testing')

    # WHEN we call convert_model_to_event_name
    event_name = EventHandler.extract_event_name_from_model(notification)

    # THEN we get the expected event name
    assert event_name == 'product_http_notification'.upper()


def test_convert_model_to_event_name_with_numbers():
    # GIVEN a model name in pascal case
    class ProductHTTPNotification123(BaseModel):
        message: str

    notification = ProductHTTPNotification123(message='testing')

    # WHEN we call convert_model_to_event_name
    event_name = EventHandler.extract_event_name_from_model(notification)

    # THEN we get the expected event name
    assert event_name == 'product_http_notification123'.upper()


def test_build_events_from_models():
    # GIVEN any Pydantic model
    class SampleNotification(BaseModel):
        message: str

    # WHEN we call build_events_from_models with all required fields
    notification = SampleNotification(message='Hello World!')
    event = EventHandler.build_events_from_models(models=[notification], event_source='sample')

    # THEN we get a list of Events
    assert type(event[0]) is Event
