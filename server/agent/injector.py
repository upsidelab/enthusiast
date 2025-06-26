from enthusiast_common.injectors import BaseInjector
from enthusiast_common.retrievers import BaseRetriever


class Injector(BaseInjector):
    def __init__(self, document_retriever: BaseRetriever, product_retriever: BaseRetriever):
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever

    @property
    def document_retriever(self) -> BaseRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseRetriever:
        return self._product_retriever
