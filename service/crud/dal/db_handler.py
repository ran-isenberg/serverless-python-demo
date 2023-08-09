from abc import ABC, ABCMeta, abstractmethod

from service.crud.dal.schemas.db import ProductEntry


class _SingletonMeta(ABCMeta):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DalHandler(ABC, metaclass=_SingletonMeta):

    @abstractmethod
    def create_product_in_db(self, product_id: str, product_name: str, product_price: int) -> ProductEntry:
        ...  # pragma: no cover
