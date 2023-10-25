from abc import ABC, abstractmethod
from typing import List

from product.crud.models.product import Product


class DbHandler(ABC):
    @abstractmethod
    def create_product(self, product: Product) -> None:
        ...  # pragma: no cover

    @abstractmethod
    def get_product(self, product_id: str) -> Product:
        ...  # pragma: no cover

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        ...  # pragma: no cover

    @abstractmethod
    def list_products(self) -> List[Product]:
        ...  # pragma: no cover
