from service.crud.dal.db_handler import DalHandler
from service.crud.dal.dynamo_dal_handler import get_dal_handler
from service.crud.dal.schemas.db import ProductEntry
from service.crud.handlers.utils.observability import logger, tracer
from service.crud.schemas.input import CreateProductRequest
from service.crud.schemas.output import CreateProductOutput


@tracer.capture_method(capture_response=False)
def handle_create_request(request: CreateProductRequest, table_name: str) -> CreateProductOutput:
    logger.info('starting to handle create request', extra={'order_item_count': request.order_item_count, 'customer_name': request.customer_name})

    dal_handler: DalHandler = get_dal_handler(table_name)
    product: ProductEntry = dal_handler.create_product_in_db(request.customer_name, request.order_item_count)
    # convert from db entry to output, they won't always be the same
    return CreateProductOutput(customer_name=product.customer_name, order_item_count=product.order_item_count, product_id=product.product_id)
