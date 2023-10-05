from product.crud.handlers.utils.observability import logger, tracer
from product.crud.integration import get_dal_handler
from product.crud.integration.db_handler import DalHandler


@tracer.capture_method(capture_response=False)
def delete_product(product_id: str, table_name: str) -> None:
    logger.info('handling delete product request')

    dal_handler: DalHandler = get_dal_handler(table_name)
    dal_handler.delete_product(product_id=product_id)
    logger.info('deleted product successfully')
