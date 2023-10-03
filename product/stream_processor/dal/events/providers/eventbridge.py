import os
from typing import TYPE_CHECKING, Optional

import boto3
import botocore.exceptions

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.dal.events.base import EventProvider
from product.stream_processor.dal.events.exceptions import ProductNotificationDeliveryError
from product.stream_processor.dal.events.models.input import Event
from product.stream_processor.dal.events.models.output import EventReceipt, EventReceiptFail, EventReceiptSuccess

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef, PutEventsResponseTypeDef


class EventBridge(EventProvider):

    def __init__(self, bus_name: str, client: Optional['EventBridgeClient'] = None):
        self.bus_name = bus_name
        self.client = client or boto3.client('events')

    def send(self, payload: list[Event]) -> EventReceipt:
        events = self.build_put_events_request(payload)

        # NOTE: we need a generator that will slice up to 10 event entries
        try:
            result = self.client.put_events(Entries=events)
        except botocore.exceptions.ClientError as exc:
            error_message = exc.response['Error']['Message']

            receipt = EventReceiptFail(receipt_id='', error='error_message', details=exc.response['ResponseMetadata'])
            raise ProductNotificationDeliveryError(f'Failed to deliver all events: {error_message}', receipts=[receipt]) from exc

        success, failed = self._collect_receipts(result)
        return EventReceipt(success=success, failed=failed)

    def build_put_events_request(self, payload: list[Event]) -> list['PutEventsRequestEntryTypeDef']:
        events: list['PutEventsRequestEntryTypeDef'] = []

        # 'Time' field is not included to be able to measure end-to-end latency later (time - created_at)
        for event in payload:
            trace_id = os.environ.get(XRAY_TRACE_ID_ENV)
            event_request = {
                'Source': event.metadata.event_source,
                'DetailType': event.metadata.event_name,
                'Detail': event.model_dump_json(),
                'EventBusName': self.bus_name,
            }

            if trace_id:
                event_request['TraceHeader'] = trace_id

            events.append(event_request)

        return events

    @staticmethod
    def _collect_receipts(result: 'PutEventsResponseTypeDef') -> tuple[list[EventReceiptSuccess], list[EventReceiptFail]]:
        successes: list[EventReceiptSuccess] = []
        fails: list[EventReceiptFail] = []

        for receipt in result['Entries']:
            error_message = receipt.get('ErrorMessage')
            event_id = receipt.get('EventId', '')

            if error_message:
                error_code = receipt.get('ErrorCode')
                fails.append(EventReceiptFail(receipt_id=event_id, error=error_message, details={'error_code': error_code}))
            else:
                successes.append(EventReceiptSuccess(receipt_id=event_id))

        # NOTE: Improve this error by correlating which entry failed to send.
        # We will fail regardless, but it'll be useful for logging and correlation later on.
        if result['FailedEntryCount'] > 0:
            raise ProductNotificationDeliveryError(f'Failed to deliver {len(fails)} events', receipts=fails)

        return successes, fails
