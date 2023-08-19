from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.exceptions import InternalServerException


class DynamoDalHandler(DalHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    # cache dynamodb connection data for no longer than 5 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_db_handler(self) -> Table:
        dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
        return dynamodb.Table(self.table_name)

    @tracer.capture_method(capture_response=False)
    def create_product_in_db(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        logger.info('trying to create a product', extra={'product_id': product_id})
        try:
            entry = ProductEntry(name=product_name, id=product_id, price=product_price)
            logger.debug('opening connection to dynamodb table', extra={'table_name': self.table_name})
            table: Table = self._get_db_handler()
            table.put_item(Item=entry.model_dump())
        except (ClientError, ValidationError) as exc:
            error_msg = 'failed to create product'
            logger.exception(error_msg, extra={'exception': str(exc)})
            raise InternalServerException(error_msg) from exc

        logger.info('finished create product', extra={'product_id': product_id})
        return entry


@lru_cache
def get_dal_handler(table_name: str) -> DalHandler:
    return DynamoDalHandler(table_name)
