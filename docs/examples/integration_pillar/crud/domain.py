from product.crud.handlers.utils.observability import logger
from product.crud.integration import get_db_handler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import CreateProductOutput


def create_product(product: Product, table_name: str):
    logger.info('handling create product request')
    db_handler = get_db_handler(table_name)
    product = Product(
        name=product.name,
        id=product.id,
        price=product.price,
    )
    db_handler.create_product(product=product)
    return CreateProductOutput(id=product.id)
