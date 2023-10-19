from product.crud.integration import get_db_handler
from product.crud.integration.db_handler import DbHandler
from product.crud.models.output import GetProductOutput
from product.crud.models.product import Product
from product.observability import logger, tracer


@tracer.capture_method(capture_response=False)
def get_product(product_id: str, table_name: str) -> GetProductOutput:
    logger.info('handling get product request')

    dal_handler: DbHandler = get_db_handler(table_name)
    product: Product = dal_handler.get_product(product_id=product_id)
    # convert from db entry to output, they won't always be the same
    logger.info('got product successfully')
    return GetProductOutput(id=product.id, price=product.price, name=product.name)
