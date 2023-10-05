from functools import lru_cache

from product.crud.integration.db_handler import DalHandler
from product.crud.integration.dynamo_dal_handler import DynamoDalHandler


@lru_cache
def get_dal_handler(table_name: str) -> DalHandler:
    return DynamoDalHandler(table_name)
