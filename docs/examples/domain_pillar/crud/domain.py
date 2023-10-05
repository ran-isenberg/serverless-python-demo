import boto3

from product.crud.handlers.utils.observability import logger
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import CreateProductOutput


def create_product(
    product_id: str,
    product_name: str,
    product_price: int,
    table_name: str,
) -> CreateProductOutput:
    logger.info('handling create product request')
    entry = Product(name=product_name, id=product_id, price=product_price)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item=entry.model_dump())

    logger.info('created product successfully')
    # convert from db entry to output, they won't always be the same
    return CreateProductOutput(id=product_id)
