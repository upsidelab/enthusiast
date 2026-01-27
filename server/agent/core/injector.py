from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.retrievers import BaseProductRetriever, BaseVectorStoreRetriever
from enthusiast_common.structures import RepositoriesInstances
from langchain_core.callbacks import BaseCallbackHandler

from agent.core.memory import SummaryChatMemory
from agent.core.memory.limited_chat_memory import LimitedChatMemory
from catalog.models import DocumentChunk


class Injector(BaseInjector):
    def __init__(
        self,
        document_retriever: BaseVectorStoreRetriever[DocumentChunk],
        product_retriever: BaseProductRetriever,
        ecommerce_platform_connector: Optional[ECommercePlatformConnector],
        repositories: RepositoriesInstances,
        chat_summary_memory: SummaryChatMemory,
        chat_limited_memory: LimitedChatMemory,
        callbacks_handler: BaseCallbackHandler,
    ):
        super().__init__(repositories)
        self._document_retriever = document_retriever
        self._product_retriever = product_retriever
        self._ecommerce_platform_connector = ecommerce_platform_connector
        self._chat_summary_memory = chat_summary_memory
        self._chat_limited_memory = chat_limited_memory
        self._callbacks_handler = callbacks_handler

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
    def chat_summary_memory(self) -> SummaryChatMemory:
        return self._chat_summary_memory

    @property
    def chat_limited_memory(self) -> LimitedChatMemory:
        return self._chat_limited_memory

    @property
    def callbacks_handler(self) -> BaseCallbackHandler:
        return self._callbacks_handler
