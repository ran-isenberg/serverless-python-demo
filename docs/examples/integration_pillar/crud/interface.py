from abc import ABC, ABCMeta, abstractmethod
from typing import List

from product.crud.dal.schemas.db import ProductEntry


class _SingletonMeta(ABCMeta):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DalHandler(ABC, metaclass=_SingletonMeta):

    @abstractmethod
    def create_product(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        ...  # pragma: no cover

    @abstractmethod
    def get_product(self, product_id: str) -> ProductEntry:
        ...  # pragma: no cover

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        ...  # pragma: no cover

    @abstractmethod
    def list_products(self) -> List[ProductEntry]:
        ...  # pragma: no cover
