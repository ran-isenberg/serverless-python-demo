import os
from typing import TYPE_CHECKING, Generator, Optional

import boto3
import botocore.exceptions

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.dal.events.base import EventProvider
from product.stream_processor.dal.events.constants import EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY
from product.stream_processor.dal.events.exceptions import ProductNotificationDeliveryError
from product.stream_processor.dal.events.functions import chunk_from_list
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
        success: list[EventReceiptSuccess] = []
        failed: list[EventReceiptFail] = []
        events = self.build_put_events_requests(payload)

        for batch in events:
            try:
                result = self.client.put_events(Entries=batch)
                ok, not_ok = self._collect_receipts(result)
                success.extend(ok)
                failed.extend(not_ok)
            except botocore.exceptions.ClientError as exc:
                error_message = exc.response['Error']['Message']

                receipt = EventReceiptFail(receipt_id='', error='error_message', details=exc.response['ResponseMetadata'])
                raise ProductNotificationDeliveryError(f'Failed to deliver all events: {error_message}', receipts=[receipt]) from exc

        return EventReceipt(success=success, failed=failed)

    def build_put_events_requests(self, payload: list[Event]) -> Generator[list['PutEventsRequestEntryTypeDef'], None, None]:
        trace_id = os.environ.get(XRAY_TRACE_ID_ENV)

        for chunk in chunk_from_list(events=payload, max_items=EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY):
            events: list['PutEventsRequestEntryTypeDef'] = []

            for event in chunk:
                # 'Time' field is not included to be able to measure end-to-end latency later (time - created_at)
                event_request = {
                    'Source': event.metadata.event_source,
                    'DetailType': event.metadata.event_name,
                    'Detail': event.model_dump_json(),
                    'EventBusName': self.bus_name,
                }

                if trace_id:
                    event_request['TraceHeader'] = trace_id

                events.append(event_request)

            yield events

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
