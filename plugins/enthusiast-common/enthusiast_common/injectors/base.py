from abc import ABC, abstractmethod

from enthusiast_common.retrievers import BaseProductRetriever, BaseVectorStoreRetriever
from enthusiast_common.structures import RepositoriesInstances, DocumentChunkDetails
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
    def chat_summary_memory(self) -> BaseMemory:
        pass

    @property
    @abstractmethod
    def chat_limited_memory(self) -> BaseMemory:
        pass
