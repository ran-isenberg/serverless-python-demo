from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from service.crud.schemas.shared_types import ProductId


class CreateProductRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    id: ProductId
    price: PositiveInt
