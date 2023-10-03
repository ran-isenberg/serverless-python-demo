from datetime import datetime
from typing import ClassVar

import pytest
from pydantic import BaseModel

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.dal.events.base import build_events_from_models, convert_model_to_event_name
from product.stream_processor.dal.events.models.input import Event, EventMetadata
from product.stream_processor.dal.events.providers.eventbridge import EventBridge


def test_eventbridge_build_put_events_from_event_payload():
    # GIVEN a list of events from a SampleNotification model
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'V1'

    notification = SampleNotification(message='test')
    events = build_events_from_models(models=[notification], event_source='test')

    # WHEN EventBridge provider builds a PutEvents request
    event_provider = EventBridge(bus_name='test_bus')
    request = event_provider.build_put_events_request(payload=events)

    # THEN EventBridge PutEvents request should match our metadata and model data
    published_event = request[0]
    event = events[0]

    assert published_event['Source'] == event.metadata.event_source
    assert published_event['Detail'] == event.model_dump_json()
    assert published_event['DetailType'] == event.metadata.event_name
    assert published_event['EventBusName'] == event_provider.bus_name


def test_eventbridge_build_put_events_from_event_payload_include_trace_header(monkeypatch: pytest.MonkeyPatch):
    # GIVEN X-Ray Trace ID is available in the environment
    trace_id = '90835161-3067-47ba-8126-fda76dfdb0b0'
    monkeypatch.setenv(XRAY_TRACE_ID_ENV, trace_id)

    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    event_bus_name = 'sample_bus'
    notification = SampleNotification(message='test')
    events = build_events_from_models(models=[notification], event_source='test')
    event_provider = EventBridge(bus_name=event_bus_name)

    # WHEN EventBridge provider builds a PutEvents request
    request = event_provider.build_put_events_request(payload=events)

    # THEN PutEvents request should include 'TraceHeader' with the available X-Ray Trace ID
    entry = request[0]
    assert entry['TraceHeader'] == trace_id
