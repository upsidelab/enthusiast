from abc import abstractmethod, ABC
from importlib import import_module
from typing import Any, Type

from django.conf import settings
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from ..repositories import BaseDataSetRepository


class LanguageModelProvider(ABC):
    STREAMING_AVAILABLE = True

    def __init__(self, model: str):
        super(LanguageModelProvider, self).__init__()
        self._model = model

    @abstractmethod
    def provide_language_model(self, callbacks: list[BaseCallbackHandler] | None = None) -> BaseLanguageModel:
        """Initializes and returns an instance of the language model.

        Returns:
            An instance of the language model for the agent.
        """
        pass

    def provide_streaming_language_model(
        self, callbacks: list[BaseCallbackHandler] | None = None, **kwargs
    ) -> BaseLanguageModel:
        raise NotImplementedError()

    @abstractmethod
    def model_name(self) -> str:
        """Returns the name of the model that will be provided.

        Returns:
            The name of the model that will be provided by this object.
        """

    @staticmethod
    @abstractmethod
    def available_models() -> list[str]:
        """Returns a list of available models.
        Returns:
            A list of available model names.
        """


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
