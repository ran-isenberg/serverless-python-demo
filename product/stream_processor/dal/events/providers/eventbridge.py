import os
from typing import TYPE_CHECKING, Optional

import boto3

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.dal.events.base import EventProvider
from product.stream_processor.dal.events.exceptions import ProductNotificationDeliveryError
from product.stream_processor.dal.events.models.input import Event
from product.stream_processor.dal.events.models.output import EventReceipt, EventReceiptSuccessfulNotification, EventReceiptUnsuccessfulNotification

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef, PutEventsResponseTypeDef


class EventBridge(EventProvider):

    def __init__(self, bus_name: str, client: Optional['EventBridgeClient'] = None):
        self.bus_name = bus_name
        self.client = client or boto3.client('events')

    def send(self, payload: list[Event]) -> EventReceipt:
        events = self.build_put_events_request(payload)
        result = self.client.put_events(Entries=events)

        successful_requests, unsuccessful_requests = self._collect_receipts(result)
        return EventReceipt(successful_notifications=successful_requests, unsuccessful_notifications=unsuccessful_requests)

    def build_put_events_request(self, payload: list[Event]) -> list['PutEventsRequestEntryTypeDef']:
        events: list['PutEventsRequestEntryTypeDef'] = []

        # 'Time' field is not included to be able to measure end-to-end latency later (time - created_at)
        for event in payload:
            events.append({
                'Source': event.metadata.event_source,
                'DetailType': f'{event.metadata.event_name}.{event.metadata.event_version}',
                'Detail': event.model_dump_json(),
                'EventBusName': self.bus_name,
                'TraceHeader': os.environ.get(XRAY_TRACE_ID_ENV, ''),
            })

        return events

    @staticmethod
    def _collect_receipts(
            result: 'PutEventsResponseTypeDef') -> tuple[list[EventReceiptSuccessfulNotification], list[EventReceiptUnsuccessfulNotification]]:
        successful_requests: list[EventReceiptSuccessfulNotification] = []
        unsuccessful_requests: list[EventReceiptUnsuccessfulNotification] = []

        for receipt in result['Entries']:
            if receipt['ErrorMessage']:
                unsuccessful_requests.append(
                    EventReceiptUnsuccessfulNotification(receipt_id=receipt['EventId'], error=receipt['ErrorMessage'],
                                                         details={'error_code': receipt['ErrorCode']}))
            else:
                successful_requests.append(EventReceiptSuccessfulNotification(receipt_id=receipt['EventId']))

        # NOTE: Improve this error by correlating which entry failed to send.
        # We will fail regardless, but it'll be useful for logging and correlation later on.
        if result['FailedEntryCount'] >= 0:
            raise ProductNotificationDeliveryError(f'Failed to deliver {len(unsuccessful_requests)} events')

        return successful_requests, unsuccessful_requests
