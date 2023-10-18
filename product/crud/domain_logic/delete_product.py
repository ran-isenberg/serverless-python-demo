from product.crud.integration import get_db_handler
from product.crud.integration.db_handler import DbHandler
from product.observability import logger, tracer


@tracer.capture_method(capture_response=False)
def delete_product(product_id: str, table_name: str) -> None:
    logger.info('handling delete product request')

    dal_handler: DbHandler = get_db_handler(table_name)
    dal_handler.delete_product(product_id=product_id)
    logger.info('deleted product successfully')
