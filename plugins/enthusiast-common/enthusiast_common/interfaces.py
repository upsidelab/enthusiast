from abc import ABC, abstractmethod

from enthusiast_common.structures import ProductDetails, DocumentDetails


class BaseProductSourcePlugin(ABC):
    def __init__(self, data_set_id, config: dict):
        self.config = config
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Fetches products from an external source.

        Returns:
            list[ProductDetails]: A list of products to be imported to the database
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
            list[DocumentDetails]: A list of documents to be imported to the database
        """
        pass
