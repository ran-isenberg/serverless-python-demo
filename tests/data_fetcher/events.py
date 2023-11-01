import boto3
import stamina
from boto3.dynamodb.conditions import Attr, Key
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import ConditionBaseImportTypeDef
from pydantic import BaseModel


class EventIntercepted(BaseModel):
    metadata: str
    receipt_id: str
    data: str


class EventFetcher:
    PK = 'pk'
    SK = 'sk'

    def __init__(self, table_name: str, event_source: str, retries: int = 3, delay: float = 1.5, jitter: float = 0.2) -> None:
        """Fetch event intercepted and stored in an Amazon DynamoDB table.

        Intercepted events are stored in a composite key:

        - pk: {event_source}
        - sk: {receipt_id}#{event_name}#{created_at}

        This helps prevent data concurrency issues like parallel tests, shared stacks, or partial test failures.

        Pros:

        - Receipt ID is known at ingestion time allowing us to guarantee a single match
        - Event source is named after the test name allowing full traceability (e.g., test_event_bridge_provider_send)

        Cons:

        - Eventual consistency might lead to polling; no guarantee to get events at first query
        - Filtering is not as flexible as WebSockets

        Parameters
        ----------
        table_name : str
            Table name with events intercepted
        event_source: str
            Event source for event intercepted
        retries: str
            Number of maximum retries to query for event
        delay: float
            Initial delay to incur before query (useful for complex operations)
        jitter: float
            Jitter to add on every retry to spread out requests more efficiently
        """
        self.table_name = table_name
        self.event_source = event_source
        self.retries = retries
        self.delay = delay
        self.jitter = jitter
        self._ddb = boto3.resource('dynamodb')
        self.table: Table = self._ddb.Table(table_name)

    def get_event(self, receipt_id: str) -> EventIntercepted:
        """Exact match query for event based on name and receipt ID

        Parameters
        ----------
        receipt_id : str
            Receipt ID for event sent

        Returns
        -------
        EventIntercepted
            Event intercepted and retrieved from DynamoDB table
        """
        key = Key(self.PK).eq(self.event_source) & Key(self.SK).begins_with(receipt_id)

        return self._fetch_event(key_expression=key)

    def get_event_by_product_id(self, product_id: str) -> EventIntercepted:
        """Get latest event by product id (stack)

        Parameters
        ----------
        product_id : str
            Product unique ID

        Returns
        -------
        EventIntercepted
            Event intercepted and retrieved from DynamoDB table
        """
        key = Key(self.PK).eq(self.event_source)
        filter_exp = Attr('data').contains(product_id)

        return self._fetch_event(key_expression=key, filter_expression=filter_exp)

    def _fetch_event(self, key_expression: ConditionBaseImportTypeDef, filter_expression: ConditionBaseImportTypeDef = None):
        query_input = {'KeyConditionExpression': key_expression}
        if filter_expression:
            query_input['FilterExpression'] = filter_expression

        for attempt in stamina.retry_context(on=ValueError, attempts=self.retries, wait_initial=self.delay, wait_jitter=self.jitter):
            with attempt:
                ret = self.table.query(**query_input)  # type: ignore[arg-type]

                if ret['Count'] == 0:
                    raise ValueError('No event found')

                item = ret['Items'][0]

        return EventIntercepted(metadata=item['metadata'], data=item['data'], receipt_id=item['receipt_id'])  # type: ignore[arg-type]
