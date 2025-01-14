from product.crud.integration import get_db_handler
from product.crud.models.output import CreateProductOutput
from product.crud.models.product import Product


def create_product(product: Product, table_name: str):
    db_handler = get_db_handler(table_name)
    db_handler.create_product(product=product)
    return CreateProductOutput(id=product.id)
