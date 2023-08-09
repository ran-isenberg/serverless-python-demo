from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from service.crud.schemas.shared_types import ProductId


class ProductEntry(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=30)]
    id: ProductId  # primary key
    price: PositiveInt
