from datetime import datetime
from typing import ClassVar

import pytest
from pydantic import BaseModel

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.dal.events.models.input import Event, EventMetadata
from product.stream_processor.dal.events.providers.eventbridge import EventBridge


def test_eventbridge_build_put_events_from_event_payload():
    # GIVEN
    class SampleNotification(BaseModel):
        message: str

        event_source: ClassVar[str] = 'test'
        event_name: ClassVar[str] = 'sample'
        event_version: ClassVar[str] = 'v1'

    event_bus_name = 'sample_bus'
    notification = SampleNotification(message='test')

    event = Event(
        data=notification,
        metadata=EventMetadata(
            event_name=SampleNotification.event_name, event_source=SampleNotification.event_source,
            event_version=SampleNotification.event_version, correlation_id='test'
        )
    )

    # WHEN
    event_provider = EventBridge(bus_name=event_bus_name)
    request = event_provider.build_put_events_request(payload=[event])

    # THEN
    entry = request[0]
    assert entry['Source'] == event.metadata.event_source
    assert entry['Detail'] == event.model_dump_json()
    assert entry['DetailType'] == f'{event.metadata.event_name}.{event.metadata.event_version}'
    assert entry['EventBusName'] == event_bus_name


def test_eventbridge_build_put_events_from_event_payload_include_trace_header(monkeypatch: pytest.MonkeyPatch):
    # GIVEN
    trace_id = '90835161-3067-47ba-8126-fda76dfdb0b0'
    monkeypatch.setenv(XRAY_TRACE_ID_ENV, trace_id)

    class SampleNotification(BaseModel):
        message: str

        event_source: ClassVar[str] = 'test'
        event_name: ClassVar[str] = 'sample'
        event_version: ClassVar[str] = 'v1'

    event_bus_name = 'sample_bus'
    notification = SampleNotification(message='test')

    event = Event(
        data=notification,
        metadata=EventMetadata(
            event_name=SampleNotification.event_name, event_source=SampleNotification.event_source,
            event_version=SampleNotification.event_version, correlation_id='test'
        )
    )

    # WHEN
    event_provider = EventBridge(bus_name=event_bus_name)
    request = event_provider.build_put_events_request(payload=[event])

    # THEN
    entry = request[0]
    assert entry['TraceHeader'] == trace_id
