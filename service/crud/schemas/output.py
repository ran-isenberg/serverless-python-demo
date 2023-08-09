from pydantic import BaseModel

from service.crud.schemas.shared_types import ProductId


class CreateProductOutput(BaseModel):
    id: ProductId
