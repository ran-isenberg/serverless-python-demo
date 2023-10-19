from typing import List

from product.crud.integration import get_db_handler
from product.crud.integration.db_handler import DbHandler
from product.crud.models.output import ListProductsOutput
from product.crud.models.product import Product
from product.observability import logger, tracer


@tracer.capture_method(capture_response=False)
def list_products(table_name: str) -> ListProductsOutput:
    logger.info('handling list products request')

    dal_handler: DbHandler = get_db_handler(table_name)
    products: List[Product] = dal_handler.list_products()
    # convert from db entry to output, they won't always be the same
    list_output = [product.model_dump() for product in products]
    logger.info('listed products successfully')
    return ListProductsOutput.model_validate({'products': list_output})
