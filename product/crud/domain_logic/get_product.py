from product.crud.handlers.utils.observability import logger, tracer
from product.crud.integration import get_dal_handler
from product.crud.integration.db_handler import DbHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import GetProductOutput


@tracer.capture_method(capture_response=False)
def get_product(product_id: str, table_name: str) -> GetProductOutput:
    logger.info('handling get product request')

    dal_handler: DbHandler = get_dal_handler(table_name)
    product: Product = dal_handler.get_product(product_id=product_id)
    # convert from db entry to output, they won't always be the same
    logger.info('got product successfully')
    return GetProductOutput(id=product.id, price=product.price, name=product.name)
