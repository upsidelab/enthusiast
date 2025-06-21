from abc import ABC, abstractmethod

from .document import BaseDocumentRetriever
from .product import BaseProductRetriever


class BaseInjector(ABC):
    @property
    @abstractmethod
    def document_retriever(self) -> BaseDocumentRetriever:
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> BaseProductRetriever:
        pass
