from enthusiast_common.retrievers import BaseVectorStoreRetriever

from agent.core.builder import AgentBuilder
from catalog.models import DocumentChunk, ProductContentChunk


class Builder(AgentBuilder):
    def _build_product_retriever(self) -> BaseVectorStoreRetriever[ProductContentChunk]:
        return self._config.retrievers.product.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )

    def _build_document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunk]:
        return self._config.retrievers.document.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )
