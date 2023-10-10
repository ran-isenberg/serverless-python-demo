import boto3
from mypy_boto3_dynamodb.service_resource import Table

from product.crud.integration.db_handler import DbHandler
from product.crud.integration.schemas.db import Product, ProductEntries


class DynamoDalHandler(DbHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    def _get_db_handler(self, table_name: str) -> Table:
        dynamodb = boto3.resource('dynamodb')
        return dynamodb.Table(table_name)

    def create_product(self, product: Product) -> None:
        table: Table = self._get_db_handler(self.table_name)
        table.put_item(Item=product.model_dump())

    def get_product(self, product_id: str) -> Product:
        table: Table = self._get_db_handler(self.table_name)
        response = table.get_item(Key={'id': product_id})
        return Product.model_validate(response.get('Item', {}))

    def list_products(self) -> list[Product]:
        table: Table = self._get_db_handler(self.table_name)
        response = table.scan(ConsistentRead=True)
        db_entries = ProductEntries.model_validate(response)
        return db_entries.Items

    def delete_product(self, product_id: str) -> None:
        return
