from importlib import import_module
from typing import Type

from enthusiast_common import EmbeddingProvider
from enthusiast_common.registry import BaseEmbeddingProviderRegistry
from enthusiast_common.repositories import BaseDataSetRepository

from agent.repositories import DjangoDataSetRepository
from pecl import settings


class EmbeddingProviderRegistry(BaseEmbeddingProviderRegistry):
    def __init__(self, data_set_repo: BaseDataSetRepository | None = None):
        providers = settings.CATALOG_EMBEDDING_PROVIDERS
        super().__init__(providers)
        self._providers = providers
        if data_set_repo is None:
            self._data_set_repo = DjangoDataSetRepository(settings.CATALOG_MODELS["data_set"])
        else:
            self._data_set_repo = data_set_repo

    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        provider_class_name = self._providers[name]
        module_name, class_name = provider_class_name.rsplit(".", 1)
        module = import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class

    def provider_for_dataset(self, data_set_id: int) -> Type[EmbeddingProvider]:
        data_set = self._data_set_repo.get_by_id(data_set_id)
        provider_class = self.provider_class_by_name(data_set.embedding_provider)
        return provider_class
