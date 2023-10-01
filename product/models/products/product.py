from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, PositiveInt
from pydantic.functional_validators import AfterValidator

from product.models.products.validators import validate_product_id

ProductId = Annotated[str, Field(min_length=36, max_length=36), AfterValidator(validate_product_id)]


class Product(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=30)]
    id: ProductId
    price: PositiveInt


class ProductNotification(BaseModel):
    product_id: ProductId
    status: Literal['ADDED', 'REMOVED', 'UPDATED']
    created_at: datetime = Field(default_factory=datetime.utcnow)
