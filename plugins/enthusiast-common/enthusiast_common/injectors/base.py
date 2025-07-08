from abc import ABC, abstractmethod

from enthusiast_common.structures import RepositoriesInstances
from langchain_core.memory import BaseMemory


class BaseInjector(ABC):
    def __init__(self, repositories: RepositoriesInstances, memory: BaseMemory):
        self.repositories = repositories
        self.memory = memory

    @property
    @abstractmethod
    def document_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass
