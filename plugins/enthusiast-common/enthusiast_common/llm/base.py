from abc import ABC, abstractmethod
from importlib import import_module
from typing import Type, Any

from django.conf import settings
from enthusiast_common import LanguageModelProvider
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from ..repositories.base import BaseDataSetRepository


class BaseLanguageModelRegistry(ABC):
    def __init__(self, providers: dict[Any, Any]):
        self._providers = providers

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[LanguageModelProvider]:
        pass

    @abstractmethod
    def provider_for_dataset(self, data_set_id: int) -> Type[LanguageModelProvider]:
        pass


class BaseDjangoSettingsModelRegistry(BaseLanguageModelRegistry):
    def __init__(self, data_set_repo: BaseDataSetRepository):
        providers = settings.CATALOG_LANGUAGE_MODEL_PROVIDERS
        super().__init__(providers)
        self._providers = providers
        self.data_set_repo = data_set_repo

    def provider_class_by_name(self, name: str) -> Type[LanguageModelProvider]:
        provider_class_name = self._providers[name]
        module_name, class_name = provider_class_name.rsplit(".", 1)
        module = import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class

    def provider_for_dataset(self, data_set_id: int) -> Type[LanguageModelProvider]:
        data_set = self.data_set_repo.get_by_id(data_set_id)
        provider_class = self.provider_class_by_name(data_set.language_model_provider)
        return provider_class


class BaseLLM:
    def __init__(
        self,
        llm_registry: BaseLanguageModelRegistry,
        data_set_repo: BaseDataSetRepository,
        callbacks: list[BaseCallbackHandler] = None,
        streaming: bool = False,
    ):
        self._llm_registry = llm_registry
        self._streaming = streaming
        self._callbacks = callbacks
        self._data_set_repo = data_set_repo

    def _get_llm_provider(self, data_set_id: int) -> Type[LanguageModelProvider]:
        return self._llm_registry.provider_for_dataset(data_set_id)

    def get_llm(
        self, provider_class: Type[LanguageModelProvider], data_set_id: int
    ) -> BaseLanguageModel:
        data_set = self._data_set_repo.get_by_id(data_set_id)
        provider = provider_class(data_set.language_model)
        if self._streaming:
            return provider.provide_streaming_language_model(callbacks=self._callbacks)
        else:
            return provider.provide_language_model(callbacks=self._callbacks)

    def create(self, data_set_id: int):
        provider_class = self._get_llm_provider(data_set_id)
        return self.get_llm(provider_class, data_set_id)
