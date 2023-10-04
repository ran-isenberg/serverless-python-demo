from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, PositiveInt
from pydantic.functional_validators import AfterValidator

from product.models.products.validators import validate_product_id

ProductId = Annotated[str, Field(min_length=36, max_length=36), AfterValidator(validate_product_id)]
"""Unique Product ID, represented and validated as a UUID string."""


class Product(BaseModel):
    """Data representation for a product.

    Parameters
    ----------
    name : str
        Product name
    id : ProductId
        Product ID (UUID string)
    price : PositiveInt
        Product price represented as a positive integer
    """
    name: Annotated[str, Field(min_length=1, max_length=30)]
    id: ProductId
    price: PositiveInt


class ProductChangeNotification(BaseModel):
    """Data representation for a notification about a product change.

    Parameters
    ----------
    product_id : ProductId
        Product ID (UUID string)
    status : Literal['ADDED', 'REMOVED', 'UPDATED']
        Product change status
    created_at : datetime
        Product change notification creation time (UTC)
    """
    product_id: ProductId
    status: Literal['ADDED', 'REMOVED', 'UPDATED']
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __version__: str = 'v1'
