from abc import ABC, abstractmethod


class BaseInjector(ABC):
    @property
    @abstractmethod
    def document_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass

    @property
    @abstractmethod
    def product_retriever(self) -> "BaseRetriever":  # noqa: F821
        pass
