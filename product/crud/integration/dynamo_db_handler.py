from datetime import datetime
from typing import List

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from product.crud.integration.db_handler import DbHandler
from product.crud.integration.models.db import ProductEntries
from product.crud.models.exceptions import InternalServerException, ProductAlreadyExistsException, ProductNotFoundException
from product.crud.models.product import Product
from product.models.products.product import ProductEntry
from product.observability import logger, tracer


class DynamoDbHandler(DbHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    # cache dynamodb connection data for no longer than 5 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_table(self, table_name: str) -> Table:
        logger.debug('opening connection to dynamodb table', table_name=table_name)
        dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    def _get_unix_time(self) -> int:
        return int(datetime.utcnow().timestamp())

    @tracer.capture_method(capture_response=False)
    def create_product(self, product: Product) -> None:
        logger.info('trying to create a product')
        entry = ProductEntry(
            id=product.id,
            name=product.name,
            price=product.price,
            created_at=self._get_unix_time(),
        )
        try:
            table = self._get_table(self.table_name)
            table.put_item(Item=entry.model_dump(), ConditionExpression='attribute_not_exists(id)')
        except ValidationError as exc:  # pragma: no cover
            error_msg = 'failed to turn input into db entry'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc
        except ClientError as exc:  # pragma: no cover
            if exc.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':  # condition attribute_not_exists
                error_msg = f'failed to create product, product {product.id} already exists'
                logger.exception(error_msg)
                raise ProductAlreadyExistsException(error_msg) from exc
            error_msg = 'failed to create product'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        logger.info('finished create product')

    @tracer.capture_method(capture_response=False)
    def get_product(self, product_id: str) -> Product:
        logger.info('trying to get a product')
        try:
            table: Table = self._get_table(self.table_name)
            response = table.get_item(
                Key={'id': product_id},
                ConsistentRead=True,
            )
            if response.get('Item') is None:  # pragma: no cover (covered in integration test)
                error_str = 'product is not found in table'
                logger.info(error_str, product_id=product_id)  # not a service error
                raise ProductNotFoundException(error_str)
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to get product from db'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        # parse to pydantic schema
        try:
            db_entry = ProductEntry.model_validate(response.get('Item', {}))
            logger.info('got item successfully')
            ret_prod = Product(id=db_entry.id, name=db_entry.name, price=db_entry.price)
        except ValidationError as exc:  # pragma: no cover
            # rare use case where items in DB don't match the schema
            error_msg = 'failed to parse product'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        return ret_prod

    @tracer.capture_method(capture_response=False)
    def delete_product(self, product_id: str) -> None:
        logger.info('trying to delete a product')
        try:
            table: Table = self._get_table(self.table_name)
            table.delete_item(Key={'id': product_id})
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to delete product from db'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        logger.info('deleted product successfully')

    @tracer.capture_method(capture_response=False)
    def list_products(self) -> List[Product]:
        logger.info('trying to list all products')
        try:
            table: Table = self._get_table(self.table_name)
            # production readiness : add pagination support
            response = table.scan(ConsistentRead=True)
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to get product from db'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        # parse to pydantic schema
        try:
            db_entries = ProductEntries.model_validate(response)
        except ValidationError as exc:  # pragma: no cover
            # rare use case where items in DB don't match the schema
            error_msg = 'failed to parse product'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        logger.info('got products successfully')
        # convert from DB entry to product model
        entries = []
        for entry in db_entries.Items:
            entries.append(Product(id=entry.id, name=entry.name, price=entry.price))
        return entries
