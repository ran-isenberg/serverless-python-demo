import boto3

from product.crud.integration.db_handler import DbHandler
from product.crud.models.product import Product
from product.models.products.product import ProductEntry


class DynamoDalHandler(DbHandler):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def create_product(self, product: Product) -> None:
        entry = ProductEntry(id=product.id, name=product.name, price=product.price, created_at=1697783194)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(self.table_name)
        table.put_item(Item=entry.model_dump())
