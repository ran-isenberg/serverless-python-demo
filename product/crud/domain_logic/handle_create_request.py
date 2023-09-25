from product.crud.dal import get_dal_handler
from product.crud.dal.db_handler import DalHandler
from product.crud.dal.schemas.db import ProductEntry
from product.crud.handlers.utils.observability import logger, tracer
from product.crud.schemas.output import CreateProductOutput, GetProductOutput


@tracer.capture_method(capture_response=False)
def handle_create_request(product_id: str, product_name: str, product_price: int, table_name: str) -> CreateProductOutput:
    logger.info('handling create product request', extra={'product_id': product_id})

    dal_handler: DalHandler = get_dal_handler(table_name)
    product: ProductEntry = dal_handler.create_product(product_id=product_id, product_name=product_name, product_price=product_price)
    # convert from db entry to output, they won't always be the same
    return CreateProductOutput(id=product.id)


@tracer.capture_method(capture_response=False)
def handle_get_request(product_id: str, table_name: str) -> GetProductOutput:
    logger.info('handling get product request', extra={'product_id': product_id})

    dal_handler: DalHandler = get_dal_handler(table_name)
    product: ProductEntry = dal_handler.get_product(product_id=product_id)
    # convert from db entry to output, they won't always be the same
    return GetProductOutput(id=product.id, price=product.price, name=product.name)
