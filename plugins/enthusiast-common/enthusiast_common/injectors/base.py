from abc import ABC, abstractmethod
from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.memory import BaseMemoryCompactor
from enthusiast_common.retrievers import BaseProductRetriever, BaseVectorStoreRetriever
from enthusiast_common.structures import RepositoriesInstances, DocumentChunkDetails
from langchain_core.chat_history import BaseChatMessageHistory


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
    def chat_history(self) -> BaseChatMessageHistory:
        pass

    @property
    def memory_compactor(self) -> Optional[BaseMemoryCompactor]:
        """Return a memory compactor, or None if not configured."""
        return None
