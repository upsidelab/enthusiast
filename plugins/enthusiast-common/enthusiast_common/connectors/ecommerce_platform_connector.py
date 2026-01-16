from abc import ABC, abstractmethod
from typing import Optional

from enthusiast_common.structures import Address, ProductDetails


class ECommercePlatformConnector(ABC):
    """This is a basic interface for a platform connector, that allows agents to interact with e-commerce systems
    though a unified interface."""

    @abstractmethod
    def create_empty_order(self) -> str:
        pass

    @abstractmethod
    def add_to_order(self, order_id: str, sku: str, quantity: int) -> bool:
        pass

    @abstractmethod
    def create_order_with_items(self, items: list[tuple[str, int]], email: Optional[str], address: Optional[Address]) -> str:
        pass

    @abstractmethod
    def get_product_by_sku(self, sku: str) -> ProductDetails:
        pass

    @abstractmethod
    def create_product(self, product_details: ProductDetails) -> bool:
        pass

    @abstractmethod
    def update_product(self, sku: str, product_details: ProductDetails) -> bool:
        pass
