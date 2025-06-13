from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Type

from django.conf import settings

from ..repositories import BaseDataSetRepository


class EmbeddingProvider(ABC):
    def __init__(self, model: str, dimensions: int):
        super(EmbeddingProvider, self).__init__()
        self._model = model
        self._dimensions = dimensions

    @abstractmethod
    def generate_embeddings(self, content: str) -> list[float]:
        """Generates an embedding vector for the specified content and returns it.

        Args:
            content (str): The input content for which the embedding vector is generated.
        """
        pass

    @staticmethod
    @abstractmethod
    def available_models() -> list[str]:
        """Returns a list of available models.

        Returns:
            A list of supported model names.
        """


class BaseEmbeddingProviderRegistry(ABC):
    def __init__(self, providers: dict[Any, Any]):
        self._providers = providers

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        pass

    @abstractmethod
    def provider_for_dataset(self, data_set_id: int) -> Type[EmbeddingProvider]:
        pass


class BaseDjangoSettingsEmbeddingRegistry(BaseEmbeddingProviderRegistry):
    def __init__(self, data_set_repo: BaseDataSetRepository):
        providers = settings.CATALOG_EMBEDDING_PROVIDERS
        super().__init__(providers)
        self._providers = providers
        self.data_set_repo = data_set_repo

    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        provider_class_name = self._providers[name]
        module_name, class_name = provider_class_name.rsplit(".", 1)
        module = import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class

    def provider_for_dataset(self, data_set_id: int) -> Type[EmbeddingProvider]:
        data_set = self.data_set_repo.get_by_id(data_set_id)
        provider_class = self.provider_class_by_name(data_set.embedding_provider)
        return provider_class
