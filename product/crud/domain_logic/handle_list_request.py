from typing import List

from product.crud.dal import get_dal_handler
from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import Product
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.output import ListProductsOutput


@tracer.capture_method(capture_response=False)
def handle_list_request(table_name: str) -> ListProductsOutput:
    logger.info('handling list products request')

    dal_handler: DalHandler = get_dal_handler(table_name)
    products: List[Product] = dal_handler.list_products()
    # convert from db entry to output, they won't always be the same
    list_output = [product.model_dump() for product in products]
    return ListProductsOutput.model_validate({'products': list_output})
