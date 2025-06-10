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

    @document_retriever.setter
    @abstractmethod
    def document_retriever(self, retriever: BaseDocumentRetriever) -> None:
        pass

    @product_retriever.setter
    @abstractmethod
    def product_retriever(self, retriever: BaseProductRetriever) -> None:
        pass


class Injector(BaseInjector):
    _product_retriever: BaseProductRetriever
    _document_retriever: BaseDocumentRetriever

    @property
    def document_retriever(self) -> BaseDocumentRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever

    @document_retriever.setter
    def document_retriever(self, retriever: BaseDocumentRetriever) -> None:
        self._document_retriever = retriever

    @product_retriever.setter
    def product_retriever(self, retriever: BaseProductRetriever) -> None:
        self._product_retriever = retriever
