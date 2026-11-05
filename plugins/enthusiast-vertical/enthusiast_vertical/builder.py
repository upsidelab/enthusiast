from typing import Optional

from enthusiast_vertical_common.connectors import ECommercePlatformConnector
from enthusiast_vertical_common.interfaces import ECommerceIntegrationPlugin
from suvereo_common.builder import AgentBuilder
from suvereo_common.config import AgentConfig

from enthusiast_vertical.injector import EcommerceInjector
from enthusiast_vertical.retrievers import DocumentRetriever, ProductRetriever


class EcommerceAgentBuilder(AgentBuilder[AgentConfig]):
    """AgentBuilder that wires an EcommerceInjector with product and document retrievers."""

    def _build_injector(self) -> EcommerceInjector:
        chat_history = self._build_chat_history()
        memory_compactor = self._build_memory_compactor(chat_history)
        product_retriever = self._build_product_retriever()
        document_retriever = self._build_document_retriever()
        ecommerce_platform_connector = self._build_ecommerce_platform_connector()
        return EcommerceInjector(
            product_retriever=product_retriever,
            document_retriever=document_retriever,
            ecommerce_platform_connector=ecommerce_platform_connector,
            repositories=self._repositories,
            chat_history=chat_history,
            memory_compactor=memory_compactor,
            tool_scratchpad=self._tool_scratchpad,
        )

    def _build_product_retriever(self) -> ProductRetriever:
        return ProductRetriever(data_set_id=self._data_set_id, llm=self._build_default_llm())

    def _build_document_retriever(self) -> DocumentRetriever:
        return DocumentRetriever(
            data_set_id=self._data_set_id,
            embeddings_registry=self._embeddings_registry,
            searcher=self._config.similarity_searcher(),
        )

    def _build_ecommerce_platform_connector(self) -> Optional[ECommercePlatformConnector]:
        if self._config.integration_plugin_resolver is None:
            return None
        resolver = self._config.integration_plugin_resolver()
        plugin = resolver.resolve(self._data_set_id, ECommerceIntegrationPlugin)
        if plugin is None:
            return None
        return plugin.build_connector()
