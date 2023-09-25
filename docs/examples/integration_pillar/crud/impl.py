import boto3
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb.service_resource import Table

from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.utils.observability import logger


class DynamoDalHandler(DalHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_db_handler(self, table_name: str) -> Table:
        dynamodb = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    def create_product(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        logger.info('trying to create a product', extra={'product_id': product_id})
        entry = ProductEntry(name=product_name, id=product_id, price=product_price)
        table: Table = self._get_db_handler(self.table_name)
        table.put_item(Item=entry.model_dump())
        logger.info('finished create product', extra={'product_id': product_id})
        return entry

    def get_product(self, product_id: str) -> ProductEntry:
        logger.info('trying to get a product', extra={'product_id': product_id})
        table: Table = self._get_db_handler(self.table_name)
        response = table.get_item(Key={'id': product_id})
        db_entry = ProductEntry.model_validate(response.get('Item', {}))
        logger.info('got item successfully', extra={'product_id': product_id})
        return db_entry
