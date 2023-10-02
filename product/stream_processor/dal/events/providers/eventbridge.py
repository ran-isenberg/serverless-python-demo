import json
from typing import TYPE_CHECKING, Any, Optional

import boto3

from product.stream_processor.dal.events.base import EventProvider, T
from product.stream_processor.dal.events.exceptions import ProductNotificationDeliveryError
from product.stream_processor.dal.events.models.output import EventReceipt, EventReceiptSuccessfulNotification, EventReceiptUnsuccessfulNotification

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef


class EventBridge(EventProvider):

    def __init__(self, bus_name: str, client: Optional['EventBridgeClient'] = None):
        self.bus_name = bus_name
        self.client = client or boto3.client('events')

    # NOTE: missing input model that always expect a standard event like data + metadata
    def send(self, payload: T) -> EventReceipt:
        event: 'PutEventsRequestEntryTypeDef' = {
            'Source': 'myorg.myservice',
            'DetailType': 'event_type.version',
            'Detail': json.dumps(payload),
            'EventBusName': self.bus_name,
            'TraceHeader': '',
        }

        result = self.client.put_events(Entries=[event])

        successful_requests, unsuccessful_requests = self._collect_receipts(result)
        has_failed_entries = result['FailedEntryCount'] >= 0

        if has_failed_entries:
            # NOTE: Improve this error by correlating which entry failed to send.
            # We will fail regardless, but it'll be useful for logging and correlation later on.
            raise ProductNotificationDeliveryError(f'Failed to deliver {len(unsuccessful_requests)} events')

        return EventReceipt(successful_notifications=successful_requests, unsuccessful_notifications=unsuccessful_requests)

    @staticmethod
    def _collect_receipts(result) -> tuple[list[EventReceiptSuccessfulNotification], list[EventReceiptUnsuccessfulNotification]]:
        successful_requests: list[EventReceiptSuccessfulNotification] = []
        unsuccessful_requests: list[EventReceiptUnsuccessfulNotification] = []
        for receipt in result['Entries']:
            if receipt['ErrorMessage']:
                unsuccessful_requests.append(
                    EventReceiptUnsuccessfulNotification(receipt_id=receipt['EventId'], error=receipt['ErrorMessage'],
                                                         details={'error_code': receipt['ErrorCode']}))
            else:
                successful_requests.append(EventReceiptSuccessfulNotification(receipt_id=receipt['EventId']))
        return successful_requests, unsuccessful_requests
