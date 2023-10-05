from product.crud.handlers.utils.observability import logger, tracer
from product.crud.integration import get_dal_handler
from product.crud.integration.db_handler import DalHandler
from product.crud.integration.schemas.db import Product
from product.crud.schemas.output import CreateProductOutput


@tracer.capture_method(capture_response=False)
def create_product(product_id: str, product_name: str, product_price: int, table_name: str) -> CreateProductOutput:
    logger.info('handling create product request', extra={'product_id': product_id})

    dal_handler: DalHandler = get_dal_handler(table_name)
    product = Product(id=product_id, name=product_name, price=product_price)
    dal_handler.create_product(product=product)
    # convert from db entry to output, they won't always be the same
    logger.info('created product successfully', extra={'product_id': product_id})
    return CreateProductOutput(id=product.id)
