from abc import ABC, abstractmethod

from .document import BaseDocumentRetriever
from .product import BaseProductRetriever


class BaseInjector(ABC):
    def __init__(self, product_retriever: BaseProductRetriever, document_retriever: BaseDocumentRetriever):
        self._product_retriever = product_retriever
        self._document_retriever = document_retriever

    @property
    @abstractmethod
    def document_retriever(self) -> BaseDocumentRetriever:
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> BaseProductRetriever:
        pass


class Injector(BaseInjector):
    @property
    def document_retriever(self) -> BaseDocumentRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever
