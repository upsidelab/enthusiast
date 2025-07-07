from abc import ABC, abstractmethod
from typing import Any, Type

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel


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
    def provider_for_dataset(self, data_set_id: Any) -> Type[LanguageModelProvider]:
        pass
