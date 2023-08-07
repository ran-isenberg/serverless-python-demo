from service.crud.schemas.shared_types import ProductId
from pydantic import BaseModel


class CreateProductOutput(BaseModel):
    id: ProductId
