from typing import List

from product.crud.dal import get_dal_handler
from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.output import ListProductsOutput


@tracer.capture_method(capture_response=False)
def handle_list_request(table_name: str) -> ListProductsOutput:
    logger.info('handling list products request')

    dal_handler: DalHandler = get_dal_handler(table_name)
    products: List[ProductEntry] = dal_handler.list_products()
    # convert from db entry to output, they won't always be the same
    outlist = []
    for product in products:
        outlist.append(product.model_dump())
    return ListProductsOutput.model_validate({'products': outlist})
