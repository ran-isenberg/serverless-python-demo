import os
from typing import TYPE_CHECKING, Generator, Optional

import boto3
import botocore.exceptions

from product.constants import XRAY_TRACE_ID_ENV
from product.stream_processor.integrations.events.base import BaseEventProvider
from product.stream_processor.integrations.events.constants import EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY
from product.stream_processor.integrations.events.exceptions import ProductChangeNotificationDeliveryError
from product.stream_processor.integrations.events.functions import chunk_from_list
from product.stream_processor.integrations.events.models.input import Event
from product.stream_processor.integrations.events.models.output import EventReceipt, EventReceiptFail, EventReceiptSuccess

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef, PutEventsResponseTypeDef


class EventBridge(BaseEventProvider):

    def __init__(self, bus_name: str, client: Optional['EventBridgeClient'] = None):
        """Amazon EventBridge provider using PutEvents API.

        See [PutEvents docs](https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html).

        Parameters
        ----------
        bus_name : str
            Name of the event bus to send events to
        client : Optional[EventBridgeClient], optional
            EventBridge boto3 client to use, by default None
        """
        self.bus_name = bus_name
        self.client = client or boto3.client('events')

    def send(self, payload: list[Event]) -> EventReceipt:
        """Sends batches of events up to maximum allowed by PutEvents API (10).

        Parameters
        ----------
        payload : list[Event]
            List of events to publish

        Returns
        -------
        EventReceipt
            Receipts for unsuccessfully and successfully published events

        Raises
        ------
        ProductChangeNotificationDeliveryError
            When one or more events could not be delivered.
        """
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
                raise ProductChangeNotificationDeliveryError(f'Failed to deliver all events: {error_message}', receipts=[receipt]) from exc

        return EventReceipt(success=success, failed=failed)

    def build_put_events_requests(self, payload: list[Event]) -> Generator[list['PutEventsRequestEntryTypeDef'], None, None]:
        """Converts a list of events into a list of PutEvents API request.

        If AWS X-Ray is enabled, it automatically includes 'TraceHeader' field in the request.

        Yields
        ------
        list['PutEventsRequestEntryTypeDef']
            List of maximum events permitted to be sent by a single PutEvents API.
        """
        trace_id = os.environ.get(XRAY_TRACE_ID_ENV)

        for chunk in chunk_from_list(events=payload, max_items=EVENTBRIDGE_PROVIDER_MAX_EVENTS_ENTRY):
            events: list['PutEventsRequestEntryTypeDef'] = []

            for event in chunk:
                # 'Time' field is not included to be able to measure end-to-end latency later (time - created_at)
                event_request: 'PutEventsRequestEntryTypeDef' = {
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
            raise ProductChangeNotificationDeliveryError(f'Failed to deliver {len(fails)} events', receipts=fails)

        return successes, fails
