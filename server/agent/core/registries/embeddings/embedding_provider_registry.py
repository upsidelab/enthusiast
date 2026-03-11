from typing import List, Type

from enthusiast_common.registry import BaseEmbeddingProviderRegistry
from enthusiast_common.registry.embeddings import EmbeddingProvider
from enthusiast_common.repositories import BaseDataSetRepository
from utils.base_registry import BaseRegistry

from agent.core.repositories import DjangoDataSetRepository
from pecl import settings


class EmbeddingProviderRegistry(BaseRegistry[EmbeddingProvider], BaseEmbeddingProviderRegistry):
    """Registry of available embedding providers registered in the system."""

    plugin_base = EmbeddingProvider

    def __init__(self, data_set_repo: BaseDataSetRepository | None = None):
        if data_set_repo is None:
            self._data_set_repo = DjangoDataSetRepository(settings.CATALOG_MODELS["data_set"])
        else:
            self._data_set_repo = data_set_repo

    def get_provider_classes(self) -> List[Type[EmbeddingProvider]]:
        """Returns all registered provider classes."""
        return [self._get_plugin_class_by_path(path) for path in self._get_plugin_paths()]

    def _get_provider_classes_by_name(self) -> dict[str, Type[EmbeddingProvider]]:
        """Returns a mapping of provider NAME to provider class."""
        return {cls.NAME: cls for cls in self.get_provider_classes()}

    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        """Looks up a provider class by its ``NAME`` attribute."""
        return self._get_provider_classes_by_name()[name]

    def provider_for_dataset(self, data_set_id: int) -> Type[EmbeddingProvider]:
        """Returns the provider class configured for the given data set."""
        data_set = self._data_set_repo.get_by_id(data_set_id)
        return self.provider_class_by_name(data_set.embedding_provider)

    @staticmethod
    def _get_plugin_paths() -> List[str]:
        """Returns the list of provider class paths from settings."""
        return settings.CATALOG_EMBEDDING_PROVIDERS
