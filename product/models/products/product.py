from datetime import datetime
from typing import Annotated, Literal, ClassVar

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

    # NOTE: consider whether this is the best place.
    # at best, keeping it close to the model it's easier to detect schema or breaking changes
    # these are not serialized when using dict(), model_dump(), or model_dump_json()
    event_name: ClassVar[str] = 'PRODUCT_CHANGE_NOTIFICATION'
    event_version: ClassVar[str] = 'v1'
