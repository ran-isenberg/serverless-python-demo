from functools import lru_cache

from product.crud.integration.db_handler import DbHandler
from product.crud.integration.dynamo_db_handler import DynamoDbHandler


@lru_cache
def get_db_handler(table_name: str) -> DbHandler:
    return DynamoDbHandler(table_name)
