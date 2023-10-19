from typing import Annotated, List

from pydantic import BaseModel, Field, PositiveInt

from product.models.products.product import ProductId


class CreateProductOutput(BaseModel):
    id: ProductId


class GetProductOutput(BaseModel):
    id: ProductId
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt


class ListProductsOutput(BaseModel):
    products: List[GetProductOutput]
