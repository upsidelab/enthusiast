from typing import Any, Type

from enthusiast_common.registry.llm import LanguageModelProvider
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from ..registry import BaseLanguageModelRegistry
from ..repositories import BaseDataSetRepository


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

    def _get_llm_provider(self, data_set_id: Any) -> Type[LanguageModelProvider]:
        return self._llm_registry.provider_for_dataset(data_set_id)

    def _get_llm(self, provider_class: Type[LanguageModelProvider], data_set_id: Any) -> BaseLanguageModel:
        data_set = self._data_set_repo.get_by_id(data_set_id)
        provider = provider_class(data_set.language_model)
        if self._streaming and provider.STREAMING_AVAILABLE:
            return provider.provide_streaming_language_model(callbacks=self._callbacks)
        else:
            return provider.provide_language_model(callbacks=self._callbacks)

    def create(self, data_set_id: Any):
        provider_class = self._get_llm_provider(data_set_id)
        return self._get_llm(provider_class, data_set_id)
