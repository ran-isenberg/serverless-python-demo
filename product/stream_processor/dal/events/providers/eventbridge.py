import json
from typing import TYPE_CHECKING, Any, Optional

import boto3

from product.stream_processor.dal.events.base import EventProvider

if TYPE_CHECKING:
    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef


class EventBridge(EventProvider):

    def __init__(self, bus_name: str, client: Optional['EventBridgeClient'] = None):
        self.bus_name = bus_name
        self.client = client or boto3.client('events')

    # NOTE: missing input model that always expect a standard event like data + metadata
    def send(self, payload: list[dict[str, Any]]):
        event: 'PutEventsRequestEntryTypeDef' = {
            'Source': 'myorg.myservice',
            'DetailType': 'event_type.version',
            'Detail': json.dumps(payload),
            'EventBusName': self.bus_name,
            'TraceHeader': '',
        }

        result = self.client.put_events(Entries=[event])

        # Temporary until we create a model for our DAL (EventReceipt)
        return {
            'success': result['FailedEntryCount'] == 0,
            'failed_entries': result['Entries'],
            'request_id': result['ResponseMetadata']['RequestId']
        }
