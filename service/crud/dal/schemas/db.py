from pydantic import BaseModel, Field, PositiveFloat
from service.crud.schemas.shared_types import ProductId

from typing import Annotated


class ProductEntry(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=30)]
    id: ProductId  # primary key
    price: PositiveFloat
