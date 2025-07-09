from abc import ABC, abstractmethod

from enthusiast_common.structures import RepositoriesInstances
from langchain_core.memory import BaseMemory


class BaseInjector(ABC):
    def __init__(self, repositories: RepositoriesInstances):
        self.repositories = repositories

    @property
    @abstractmethod
    def document_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass

    @property
    @abstractmethod
    def chat_summary_memory(self) -> BaseMemory:
        pass

    @property
    @abstractmethod
    def chat_limited_memory(self) -> BaseMemory:
        pass
