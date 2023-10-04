from uuid import uuid4

from pydantic import BaseModel

from product.stream_processor.dal.events.constants import DEFAULT_EVENT_VERSION
from product.stream_processor.dal.events.functions import build_events_from_models, convert_model_to_event_name


def test_model_to_standard_event():
    # GIVEN a model with __version__ set
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    notification = SampleNotification(message='testing')
    event_source = 'test'

    # WHEN we convert to an event
    event = build_events_from_models(models=[notification], event_source=event_source)[0]

    # THEN the event should contain our notification in `.data`, all metadata under `.metadata`
    # infer the event version from the model, event name infers model name from PascalCase to SNAKE_CASE_UPPER
    assert event.data == notification
    assert event.metadata.event_source == event_source
    assert event.metadata.event_version == notification.__version__
    assert event.metadata.event_name == convert_model_to_event_name(notification.__class__.__name__)
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
    event = build_events_from_models(models=[notification], event_source=event_source, correlation_id=correlation_id)[0]

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
    event = build_events_from_models(models=[notification], event_source=event_source, metadata=metadata)[0]

    # THEN we should have additional metadata included in the final event
    assert metadata.items() <= event.metadata.model_dump().items()


def test_model_without_version_to_standard_event():
    # GIVEN a model without __version__ set
    class SampleNotification(BaseModel):
        message: str

    notification = SampleNotification(message='testing')
    event_source = 'test'

    # WHEN we convert to an event
    event = build_events_from_models(models=[notification], event_source=event_source)[0]

    # THEN we should add a default v1 version
    assert event.metadata.event_version == DEFAULT_EVENT_VERSION
