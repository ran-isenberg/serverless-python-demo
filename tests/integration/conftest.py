import os
from datetime import datetime
from typing import Generator

import boto3
import pytest
from pydantic import BaseModel

from infrastructure.product.constants import (
    IDEMPOTENCY_TABLE_NAME_OUTPUT,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
    STREAM_PROCESSOR_TEST_EVENT_BUS_NAME_OUTPUT,
    STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT,
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


@pytest.fixture(scope='session')
def test_events_table():
    return get_stack_output(STREAM_PROCESSOR_TEST_TABLE_NAME_OUTPUT)


@pytest.fixture(scope='session')
def event_bus():
    return get_stack_output(STREAM_PROCESSOR_TEST_EVENT_BUS_NAME_OUTPUT)


@pytest.fixture(scope='module')
def add_product_entry_to_db(table_name: str) -> Generator[Product, None, None]:
    clear_table(table_name)
    product = ProductEntry(id=generate_product_id(), price=1, name='test', created_at=int(datetime.utcnow().timestamp()))
    table = boto3.resource('dynamodb').Table(table_name)
    table.put_item(Item=product.model_dump())
    yield Product(id=product.id, name=product.name, price=product.price)
    table.delete_item(Key={'id': product.id})
