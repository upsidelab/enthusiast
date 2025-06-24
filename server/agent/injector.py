from enthusiast_common.injectors import BaseInjector, BaseProductRetriever, BaseDocumentRetriever


class Injector(BaseInjector):
    def __init__(self, document_retriever: BaseDocumentRetriever, product_retriever: BaseProductRetriever):
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever

    @property
    def document_retriever(self) -> BaseDocumentRetriever:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever
