from product.crud.dal import get_dal_handler
from product.crud.dal.db_handler import DalHandler
from product.crud.handlers.utils.observability import logger, tracer


@tracer.capture_method(capture_response=False)
def handle_delete_request(product_id: str, table_name: str) -> None:
    logger.info('handling get product request', extra={'product_id': product_id})

    dal_handler: DalHandler = get_dal_handler(table_name)
    dal_handler.delete_product(product_id=product_id)
