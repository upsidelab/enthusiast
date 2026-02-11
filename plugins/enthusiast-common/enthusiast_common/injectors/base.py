from abc import ABC, abstractmethod
from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.retrievers import BaseProductRetriever, BaseVectorStoreRetriever
from enthusiast_common.structures import DocumentChunkDetails, RepositoriesInstances
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.memory import BaseMemory


class BaseInjector(ABC):
    def __init__(self, repositories: RepositoriesInstances):
        self.repositories = repositories

    @property
    @abstractmethod
    def document_retriever(self) -> BaseVectorStoreRetriever[DocumentChunkDetails]:
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> BaseProductRetriever:
        pass

    @property
    @abstractmethod
    def ecommerce_platform_connector(self) -> Optional[ECommercePlatformConnector]:
        pass

    @property
    @abstractmethod
    def chat_summary_memory(self) -> BaseMemory:
        pass

    @property
    @abstractmethod
    def chat_limited_memory(self) -> BaseMemory:
        pass

    @property
    @abstractmethod
    def callbacks_handler(self) -> BaseCallbackHandler:
        pass
