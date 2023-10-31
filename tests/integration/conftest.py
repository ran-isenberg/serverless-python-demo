import os
import time
from datetime import datetime
from typing import Generator

import boto3
import pytest
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import BaseModel

from infrastructure.product.constants import (
    IDEMPOTENCY_TABLE_NAME_OUTPUT,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
    STREAM_PROCESSOR_EVENT_BUS_NAME_OUTPUT,
    STREAM_TESTS_TABLE_NAME_OUTPUT,
    TABLE_NAME_OUTPUT,
)
from product.crud.models.product import Product
from product.models.products.product import ProductEntry
from tests.crud_utils import clear_table, generate_product_id
from tests.utils import get_stack_output


class EventIntercepted(BaseModel):
    metadata: str
    receipt_id: str
    data: str


@pytest.fixture(scope='session', autouse=True)
def init():
    os.environ[POWERTOOLS_SERVICE_NAME] = SERVICE_NAME
    os.environ[POWER_TOOLS_LOG_LEVEL] = 'DEBUG'
    os.environ['REST_API'] = 'https://www.ranthebuilder.cloud/api'
    os.environ['ROLE_ARN'] = 'arn:partition:service:region:account-id:resource-type:resource-id'
    os.environ['AWS_DEFAULT_REGION'] = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')  # used for appconfig mocked boto calls
    os.environ['TABLE_NAME'] = get_stack_output(TABLE_NAME_OUTPUT)
    os.environ['IDEMPOTENCY_TABLE_NAME'] = get_stack_output(IDEMPOTENCY_TABLE_NAME_OUTPUT)


@pytest.fixture(scope='session', autouse=True)
def table_name():
    return os.environ['TABLE_NAME']


@pytest.fixture(scope='session', autouse=True)
def test_events_table():
    return get_stack_output(STREAM_TESTS_TABLE_NAME_OUTPUT)


@pytest.fixture(scope='session', autouse=True)
def event_bus():
    return get_stack_output(STREAM_PROCESSOR_EVENT_BUS_NAME_OUTPUT)


@pytest.fixture(scope='module', autouse=True)
def add_product_entry_to_db(table_name: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product = ProductEntry(id=generate_product_id(), price=1, name='test', created_at=int(datetime.utcnow().timestamp()))
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield Product(id=product.id, name=product.name, price=product.price)
    table.delete_item(Key={'id': product.id})


def get_event_from_table(table_name: str, event_source: str, event_name: str, receipt_id: str) -> EventIntercepted:
    """Fetch event intercepted and stored in DynamoDB table.

    Intercepted events are stored with a primary key named: {event_source}#{event_name}#{receipt_id}.

    This helps prevent data concurrency issues like parallel tests, shared stacks, or partial test failures.

    Pros:

    - Receipt ID is known at ingestion time allowing us to guarantee a single match
    - Event source is named after the test name allowing full traceability (e.g., test_event_bridge_provider_send)

    Cons:

    - Testing a batch of events is inefficient with this function (N calls)
    - While queries are optimized, eventual consistency might lead to polling; not as efficient as WebSockets

    Parameters
    ----------
    table_name : str
        Table name with events intercepted
    event_source
        Event source for event intercepted
    event_name
        Event name
    receipt_id
        Receipt ID for event ingested earlier

    Returns
    -------
    EventIntercepted
        Event intercepted and retrieved from DynamoDB table
    """
    pk = f'{event_source}#{event_name}#{receipt_id}'

    ddb = boto3.resource('dynamodb')
    table: Table = ddb.Table(table_name)

    time.sleep(1)  # TODO: replace this with polling logic
    ret = table.query(KeyConditionExpression='pk = :pk', ExpressionAttributeValues={':pk': pk})

    item = ret['Items'][0]  # todo: allow multiple events to be batched
    return EventIntercepted(metadata=item['metadata'], data=item['data'], receipt_id=item['receipt_id'])  # type: ignore[arg-type]
