import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.exceptions import InternalServerException, ProductNotFoundException


class DynamoDalHandler(DalHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    # cache dynamodb connection data for no longer than 5 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_db_handler(self, table_name: str) -> Table:
        logger.debug('opening connection to dynamodb table', extra={'table_name': table_name})
        dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    @tracer.capture_method(capture_response=False)
    def create_product(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        logger.info('trying to create a product', extra={'product_id': product_id})
        try:
            entry = ProductEntry(name=product_name, id=product_id, price=product_price)
            logger.debug('opening connection to dynamodb table', extra={'table_name': self.table_name})
            table: Table = self._get_db_handler(self.table_name)
            table.put_item(Item=entry.model_dump())
        except (ClientError, ValidationError) as exc:
            error_msg = 'failed to create product'
            logger.exception(error_msg, extra={'exception': str(exc)})
            raise InternalServerException(error_msg) from exc

        logger.info('finished create product', extra={'product_id': product_id})
        return entry

    @tracer.capture_method(capture_response=False)
    def get_product(self, product_id: str) -> ProductEntry:
        logger.info('trying to get a product', extra={'product_id': product_id})
        try:
            table: Table = self._get_db_handler(self.table_name)
            response = table.get_item(Key={'id': product_id})
            if response.get('Item') is None:  # pragma: no cover (covered in integration test)
                error_str = 'product is not found in table'
                logger.info(error_str, extra={'product_id': product_id})  # not a service error
                raise ProductNotFoundException(error_str)
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to get product from db'
            logger.exception(error_msg, extra={'exception': str(exc)})
            raise InternalServerException(error_msg) from exc

        # parse to pydantic schema
        try:
            db_entry = ProductEntry.model_validate(response.get('Item', {}))
        except ValidationError as exc:  # pragma: no cover
            # rare use case where items in DB don't match the schema
            error_msg = 'failed to parse product'
            logger.exception(error_msg, extra={'exception': str(exc)})
            raise InternalServerException(error_msg) from exc

        logger.info('got item successfully', extra={'product_id': product_id})
        return db_entry

    @tracer.capture_method(capture_response=False)
    def delete_product(self, product_id: str) -> None:
        logger.info('trying to delete a product', extra={'product_id': product_id})
        try:
            table: Table = self._get_db_handler(self.table_name)
            table.delete_item(Key={'id': product_id})
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to delete product from db'
            logger.exception(error_msg, extra={'exception': str(exc)})
            raise InternalServerException(error_msg) from exc

        logger.info('deleted product successfully', extra={'product_id': product_id})
