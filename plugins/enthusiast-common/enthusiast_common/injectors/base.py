from abc import ABC, abstractmethod

from enthusiast_common.structures import RepositoriesInstances


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
