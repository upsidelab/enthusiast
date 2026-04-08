from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.memory import BaseMemoryCompactor
from enthusiast_common.retrievers import BaseProductRetriever, BaseVectorStoreRetriever
from enthusiast_common.structures import RepositoriesInstances
from langchain_core.chat_history import BaseChatMessageHistory

from agent.core.memory import LLMMemoryCompactor, PersistentChatHistory
from catalog.models import DocumentChunk


class Injector(BaseInjector):
    def __init__(
        self,
        document_retriever: BaseVectorStoreRetriever[DocumentChunk],
        product_retriever: BaseProductRetriever,
        ecommerce_platform_connector: Optional[ECommercePlatformConnector],
        repositories: RepositoriesInstances,
        chat_history: PersistentChatHistory,
        memory_compactor: Optional[LLMMemoryCompactor] = None,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._ecommerce_platform_connector = ecommerce_platform_connector
        self._chat_history = chat_history
        self._memory_compactor = memory_compactor

    @property
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunk]:
        return self._document_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever

    @property
    def ecommerce_platform_connector(self) -> Optional[ECommercePlatformConnector]:
        return self._ecommerce_platform_connector

    @property
    def chat_history(self) -> BaseChatMessageHistory:
        return self._chat_history

    @property
    def memory_compactor(self) -> Optional[BaseMemoryCompactor]:
        return self._memory_compactor
