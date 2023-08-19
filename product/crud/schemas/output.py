from pydantic import BaseModel

from product.crud.schemas.shared_types import ProductId


class CreateProductOutput(BaseModel):
    id: ProductId
