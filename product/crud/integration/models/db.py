from typing import List

from pydantic import BaseModel

from product.models.products.product import ProductEntry


class ProductEntries(BaseModel):
    Items: List[ProductEntry]
