from abc import ABC, abstractmethod
from typing import Optional

from enthusiast_common.structures import Address, ProductDetails, ProductUpdateDetails


class ECommercePlatformConnector(ABC):
    """This is a basic interface for a platform connector, that allows agents to interact with e-commerce systems
    though a unified interface."""

    required_product_create_fields: set[str] = set()

    @abstractmethod
    def create_empty_order(self, email: Optional[str] = None, address: Optional[Address] = None) -> str:
        pass

    @abstractmethod
    def add_to_order(self, order_id: str, sku: str, quantity: int) -> bool:
        pass

    @abstractmethod
    def create_order_with_items(self, items: list[tuple[str, int]], email: Optional[str] = None, address: Optional[Address] = None) -> str:
        pass

    @abstractmethod
    def get_product_by_sku(self, sku: str) -> Optional[ProductDetails]:
        pass

    @abstractmethod
    def create_product(self, product_details: ProductDetails) -> str:
        pass

    @abstractmethod
    def update_product(self, sku: str, product_details: ProductUpdateDetails) -> bool:
        pass

    @abstractmethod
    def get_admin_url_for_order_id(self, order_id: str) -> str:
        pass

    def _validate_create_product_data(self, product: ProductDetails) -> None:
        missing = [
            field for field in self.required_product_create_fields
            if getattr(product, field) is None
        ]

        if missing:
            raise ValueError(f"Missing required product fields: {missing}")
