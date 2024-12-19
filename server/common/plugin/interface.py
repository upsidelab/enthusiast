from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar


@dataclass
class ProductDetails:
    entry_id: str
    name: str
    slug: str
    description: str
    sku: str
    properties: str
    categories: str
    price: float


@dataclass
class DocumentDetails:
    url: str
    title: str
    content: str


ItemData = TypeVar("ItemData", ProductDetails, DocumentDetails)


class BaseProductSourcePlugin(ABC):
    def __init__(self, data_set_id, config: dict):
        self.config = config
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Fetches products from an external source.

        Returns:
            list[ProductDetails]: Each dict represents a product item.
        """
        pass


class BaseDocumentSourcePlugin(ABC):
    def __init__(self, data_set_id, config: dict):
        self.config = config
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[DocumentDetails]:
        """Fetches documents from an external system.

        Returns:
            list[DocumentDetails]: Each dict represents a document.
        """
        pass
