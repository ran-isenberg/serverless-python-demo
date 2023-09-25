from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from product.crud.schemas.shared_types import ProductId


class CreateProductOutput(BaseModel):
    id: ProductId


class GetProductOutput(BaseModel):
    id: ProductId
    name: Annotated[str, Field(min_length=1, max_length=20)]
    price: PositiveInt
