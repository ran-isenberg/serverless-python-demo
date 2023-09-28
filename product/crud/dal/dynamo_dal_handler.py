from typing import List

import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache, cached
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import Product, ProductEntries
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.exceptions import InternalServerException, ProductAlreadyExistsException, ProductNotFoundException

# from product.crud.dal.idempotency import IDEMPOTENCY_CONFIG, IDEMPOTENCY_LAYER
# from aws_lambda_powertools.utilities.idempotency.serialization.pydantic import PydanticSerializer
# from aws_lambda_powertools.utilities.idempotency import idempotent_function


class DynamoDalHandler(DalHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    # cache dynamodb connection data for no longer than 5 minutes
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    def _get_db_handler(self, table_name: str) -> Table:
        logger.debug('opening connection to dynamodb table', extra={'table_name': table_name})
        dynamodb: DynamoDBServiceResource = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    # @idempotent_function(
    #    data_keyword_argument='product',
    #    config=IDEMPOTENCY_CONFIG,
    #    persistence_store=IDEMPOTENCY_LAYER,
    #    output_serializer=PydanticSerializer,
    # )
    @tracer.capture_method(capture_response=False)
    def create_product(self, product: Product) -> None:
        logger.info('trying to create a product', extra={'product_id': product.id})
        try:
            table: Table = self._get_db_handler(self.table_name)
            table.put_item(Item=product.model_dump(), ConditionExpression='attribute_not_exists(id)')
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

        logger.info('finished create product', extra={'product_id': product.id})

    @tracer.capture_method(capture_response=False)
    def get_product(self, product_id: str) -> Product:
        logger.info('trying to get a product', extra={'product_id': product_id})
        try:
            table: Table = self._get_db_handler(self.table_name)
            response = table.get_item(
                Key={'id': product_id},
                ConsistentRead=True,
            )
            if response.get('Item') is None:  # pragma: no cover (covered in integration test)
                error_str = 'product is not found in table'
                logger.info(error_str, extra={'product_id': product_id})  # not a service error
                raise ProductNotFoundException(error_str)
        except ClientError as exc:  # pragma: no cover (covered in integration test)
            error_msg = 'failed to get product from db'
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        # parse to pydantic schema
        try:
            db_entry = Product.model_validate(response.get('Item', {}))
        except ValidationError as exc:  # pragma: no cover
            # rare use case where items in DB don't match the schema
            error_msg = 'failed to parse product'
            logger.exception(error_msg)
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
            logger.exception(error_msg)
            raise InternalServerException(error_msg) from exc

        logger.info('deleted product successfully', extra={'product_id': product_id})

    @tracer.capture_method(capture_response=False)
    def list_products(self) -> List[Product]:
        logger.info('trying to list all products')
        try:
            table: Table = self._get_db_handler(self.table_name)
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
        return db_entries.Items
