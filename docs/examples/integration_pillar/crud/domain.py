from product.crud.handlers.utils.observability import logger
from product.crud.integration import get_dal_handler
from product.crud.integration.db_handler import DbHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import CreateProductOutput


def handle_create_request(product_id: str, product_name: str, product_price: int, table_name: str) -> CreateProductOutput:
    logger.info('handling create product request', product_id=product_id)

    dal_handler: DbHandler = get_dal_handler(table_name)
    product = Product(id=product_id, name=product_name, price=product_price)
    dal_handler.create_product(product=product)
    # convert from db entry to output, they won't always be the same
    return CreateProductOutput(id=product.id)
