from abc import ABC, abstractmethod
from typing import Any, Type

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from ..structures import BaseFileContent, BaseImageContent, FileTypes, LLMFile


class LanguageModelProvider(ABC):
    """Base class for language model providers.

    Subclasses must set the ``NAME`` class attribute to a human-readable
    provider name (e.g. ``"OpenAI"``).  This value is used for display
    in the UI and for looking up the provider in the registry.
    """

    NAME: str = None
    STREAMING_AVAILABLE = True
    STREAMING_REQUIRES_MESSAGE_BUFFERING: bool = False

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

    @classmethod
    def prepare_files_objects(cls, files_objects: list[LLMFile]):
        objects = []
        for file in files_objects:
            if file.file_category == FileTypes.FILE.value:
                objects.append(cls.prepare_file_object(file))
            else:
                objects.append(cls.prepare_image_object(file))
        return objects

    @staticmethod
    @abstractmethod
    def prepare_image_object(file_object: LLMFile) -> BaseImageContent:
        pass

    @staticmethod
    @abstractmethod
    def prepare_file_object(file_object: LLMFile) -> BaseFileContent:
        pass


class BaseLanguageModelRegistry(ABC):
    """Registry of available language model providers.

    Subclasses must implement ``_get_plugin_paths`` to return the list of
    class paths from settings and ``provider_for_dataset`` to resolve a
    provider for a given data set.
    """

    @abstractmethod
    def get_provider_classes(self) -> list[Type[LanguageModelProvider]]:
        """Returns all registered provider classes."""

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[LanguageModelProvider]:
        """Looks up a provider class by its ``NAME`` attribute."""

    @abstractmethod
    def provider_for_dataset(self, data_set_id: Any) -> Type[LanguageModelProvider]:
        """Returns the provider class configured for the given data set."""
