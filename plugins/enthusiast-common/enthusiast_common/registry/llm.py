from abc import ABC, abstractmethod
from typing import Any, Type

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel

from ..config.prompts import BaseFileContent, BaseImageContent
from ..structures import FileTypes, LLMFile


class LanguageModelProvider(ABC):
    FILE_KEY_PREFIX = "file_"
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

    @classmethod
    def prepare_files_objects(cls, files_objects: list[LLMFile], data_placeholder: bool = True):
        pass
        objects = []
        for file in files_objects:
            if file.file_category == FileTypes.FILE:
                objects.append(cls.prepare_file_object(file, data_placeholder))
            else:
                objects.append(cls.prepare_image_object(file, data_placeholder))
        return objects

    @staticmethod
    @abstractmethod
    def prepare_image_object(file_object: LLMFile, data_placeholder: bool) -> BaseImageContent:
        pass

    @staticmethod
    @abstractmethod
    def prepare_file_object(file_object: LLMFile, data_placeholder: bool) -> BaseFileContent:
        pass


class BaseLanguageModelRegistry(ABC):
    def __init__(self, providers: dict[Any, Any]):
        self._providers = providers

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[LanguageModelProvider]:
        pass

    @abstractmethod
    def provider_for_dataset(self, data_set_id: Any) -> Type[LanguageModelProvider]:
        pass
