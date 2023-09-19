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
    def _get_db_handler(self) -> Table:
        dynamodb = boto3.resource('dynamodb')
        return dynamodb.Table(self.table_name)

    def create_product_in_db(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        logger.info('trying to create a product', extra={'product_id': product_id})
        entry = ProductEntry(name=product_name, id=product_id, price=product_price)
        table: Table = self._get_db_handler()
        table.put_item(Item=entry.model_dump())
        logger.info('finished create product', extra={'product_id': product_id})
        return entry


def get_dal_handler(table_name: str) -> DalHandler:
    return DynamoDalHandler(table_name)
