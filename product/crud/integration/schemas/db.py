from typing import List

from pydantic import BaseModel

from product.models.products.product import Product


class ProductEntries(BaseModel):
    Items: List[Product]
