import boto3

from product.crud.models.output import CreateProductOutput
from product.crud.models.product import Product
from product.observability import logger


def create_product(
    product: Product,
    table_name: str,
) -> CreateProductOutput:
    logger.info('handling create product request')
    entry = Product(name=product.name, id=product.id, price=product.price)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item=entry.model_dump())

    logger.info('created product successfully')
    # convert from db entry to output, they won't always be the same
    return CreateProductOutput(id=product.id)
