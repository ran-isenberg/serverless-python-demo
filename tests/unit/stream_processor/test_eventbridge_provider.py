from uuid import uuid4

import boto3
import pytest
from botocore import stub
from pydantic import BaseModel

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.integrations.events.constants import EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY
from product.stream_processor.integrations.events.event_handler import EventHandler
from product.stream_processor.integrations.events.exceptions import ProductChangeNotificationDeliveryError
from product.stream_processor.integrations.events.providers.eventbridge import EventBridge


def test_eventbridge_build_put_events_from_event_payload():
    # GIVEN a list of events from a SampleNotification model
    class SampleNotification(BaseModel):
        message: str

        __version__ = 'V1'

    notification = SampleNotification(message='test')
    events = EventHandler.build_events_from_models(models=[notification], event_source='test')

    # WHEN EventBridge provider builds a PutEvents request
    event_provider = EventBridge(bus_name='test_bus')
    requests = event_provider.build_put_events_requests(payload=events)

    # THEN EventBridge PutEvents request should match our metadata and model data
    request = next(requests)[0]
    event = events[0]

    assert request['Source'] == event.metadata.event_source
    assert request['Detail'] == event.model_dump_json()
    assert request['DetailType'] == event.metadata.event_name
    assert request['EventBusName'] == event_provider.bus_name


def test_eventbridge_build_put_events_from_event_payload_include_trace_header(monkeypatch: pytest.MonkeyPatch):
    # GIVEN X-Ray Trace ID is available in the environment
    trace_id = '90835161-3067-47ba-8126-fda76dfdb0b0'
    monkeypatch.setenv(XRAY_TRACE_ID_ENV, trace_id)

    class SampleNotification(BaseModel):
        message: str

        __version__ = 'v1'

    event_bus_name = 'sample_bus'
    notification = SampleNotification(message='test')
    events = EventHandler.build_events_from_models(models=[notification], event_source='test')
    event_provider = EventBridge(bus_name=event_bus_name)

    # WHEN EventBridge provider builds a PutEvents request
    requests = event_provider.build_put_events_requests(payload=events)

    # THEN PutEvents request should include 'TraceHeader' with the available X-Ray Trace ID
    entry = next(requests)[0]
    assert entry['TraceHeader'] == trace_id


def test_eventbridge_build_put_events_respect_max_entries_limit():
    # GIVEN an even number of events to be sent to EventBridge PutEvents API that are higher than 10 (limit)
    class SampleNotification(BaseModel):
        message: str

    number_of_events = 20

    notifications = [SampleNotification(message='test') for _ in range(number_of_events)]
    events = EventHandler.build_events_from_models(models=notifications, event_source='test')

    # WHEN EventBridge provider builds a PutEvents request
    requests = EventBridge(bus_name='test_bus').build_put_events_requests(payload=events)

    # THEN we should have a generator with two batches of the maximum permitted entry (EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY)
    first_batch = next(requests)
    second_batch = next(requests)

    assert len(first_batch) == EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY
    assert len(second_batch) == EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY
    assert len(list(requests)) == 0


def test_eventbridge_put_events_with_stubber():
    # GIVEN a list of events from a SampleNotification model and an expected PutEvents request
    class SampleNotification(BaseModel):
        message: str

    event_bus_name = 'sample_bus'
    event_source = 'test'

    notification = SampleNotification(message='testing')
    events = EventHandler.build_events_from_models(models=[notification], event_source=event_source)
    event = events[0]

    put_events_request = {
        'Entries': [{
            'Source': event_source,
            'DetailType': event.metadata.event_name,
            'Detail': event.model_dump_json(),
            'EventBusName': event_bus_name
        }]
    }

    put_events_response = {
        'Entries': [{
            'EventId': f'{uuid4()}',
        }],
        'FailedEntryCount': 0
    }

    # WHEN EventBridge receives a stubbed client and send the event payload
    client = boto3.client('events')
    stubber = stub.Stubber(client)
    stubber.add_response(method='put_events', expected_params=put_events_request, service_response=put_events_response)
    stubber.activate()

    event_provider = EventBridge(bus_name=event_bus_name, client=client)
    event_provider.send(payload=events)

    # THEN we should use the stubbed client to send the events
    # it should lead to no parameter validation error, runtime error on response manipulation syntax errors

    stubber.assert_no_pending_responses()
    stubber.deactivate()


def test_eventbridge_put_events_with_stubber_partial_failure():
    # GIVEN a list of events from a SampleNotification model and an expected PutEvents request
    class SampleNotification(BaseModel):
        message: str

    event_bus_name = 'sample_bus'
    event_source = 'test'

    notification = SampleNotification(message='testing')
    events = EventHandler.build_events_from_models(models=[notification], event_source=event_source)
    event = events[0]

    expected_failure_count = 1
    put_events_request = {
        'Entries': [{
            'Source': event_source,
            'DetailType': event.metadata.event_name,
            'Detail': event.model_dump_json(),
            'EventBusName': event_bus_name
        }]
    }

    put_events_response = {
        'Entries': [
            {
                'EventId': f'{uuid4()}',
            },
            {
                # https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html#API_PutEvents_Errors
                'ErrorCode': 'InternalException',
                'ErrorMessage': 'An internal error occurred'
            }
        ],
        'FailedEntryCount': expected_failure_count
    }

    # WHEN EventBridge receives a stubbed client with at least one FailedEntryCount
    client = boto3.client('events')
    stubber = stub.Stubber(client)
    stubber.add_response(method='put_events', expected_params=put_events_request, service_response=put_events_response)
    stubber.activate()

    event_provider = EventBridge(bus_name=event_bus_name, client=client)

    with pytest.raises(ProductChangeNotificationDeliveryError) as exc:
        event_provider.send(payload=events)

    # THEN we should receive a ProductNotificationDeliveryError along with its receipts
    stubber.assert_no_pending_responses()
    stubber.deactivate()

    assert len(exc.value.receipts) == expected_failure_count


def test_eventbridge_put_events_with_stubber_service_failure():
    # GIVEN a list of events from a SampleNotification model and an expected PutEvents request
    class SampleNotification(BaseModel):
        message: str

    event_bus_name = 'sample_bus'
    event_source = 'test'

    notification = SampleNotification(message='testing')
    events = EventHandler.build_events_from_models(models=[notification], event_source=event_source)

    # WHEN EventBridge receives a stubbed client with at least one FailedEntryCount
    client = boto3.client('events')
    stubber = stub.Stubber(client)
    stubber.add_client_error(method='put_events', http_status_code=500, service_error_code='InternalException', service_message='Oops')
    stubber.activate()

    event_provider = EventBridge(bus_name=event_bus_name, client=client)

    with pytest.raises(ProductChangeNotificationDeliveryError) as exc:
        event_provider.send(payload=events)

    # THEN we should receive a ProductNotificationDeliveryError along with its receipts
    stubber.assert_no_pending_responses()
    stubber.deactivate()

    assert len(exc.value.receipts) == 1
