from abc import ABC, abstractmethod

from enthusiast_common import ProductDetails
from .base import BaseRetriever


class BaseProductRetriever(BaseRetriever, ABC):
    @abstractmethod
    def find_products_matching_query(self, user_query: str) -> list[ProductDetails]:
        pass

    @abstractmethod
    def get_sample_products_json(self) -> str:
        pass
