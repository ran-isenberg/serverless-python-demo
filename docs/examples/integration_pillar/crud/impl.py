import boto3

from product.crud.integration.db_handler import DbHandler
from product.crud.integration.schemas.db import Product


class DynamoDalHandler(DbHandler):

    def __init__(self, table_name: str):
        self.table_name = table_name

    def create_product(self, product: Product) -> None:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(self.table_name)
        table.put_item(Item=product.model_dump())
