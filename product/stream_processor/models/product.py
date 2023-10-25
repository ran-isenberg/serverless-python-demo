from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from product.models.products.product import ProductId

# schemas here are shared between both handler and domain layer of the stream processor


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
