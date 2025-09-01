from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from enthusiast_common.structures import DocumentDetails, ProductDetails
from enthusiast_common.utils import RequiredFieldsModel, validate_required_vars
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel


class ExtraArgsClassBaseMeta(ABCMeta):
    REQUIRED_VARS = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not namespace.get("__abstract__", False):
            return validate_required_vars(cls, name, cls.REQUIRED_VARS)
        return cls


class SourceExtraArgsClassBaseMeta(ExtraArgsClassBaseMeta):
    REQUIRED_VARS = {
        "CONFIGURATION_ARGS": RequiredFieldsModel,
    }


class SourceExtraArgsClassBase(metaclass=SourceExtraArgsClassBaseMeta):
    __abstract__ = True

    def set_runtime_arguments(self, runtime_arguments: Any) -> None:
        for key, value in runtime_arguments.items():
            class_field_key = key.upper()
            field = getattr(self, class_field_key)
            if field is None:
                continue
            setattr(self, key.upper(), field(**value))


class ProductSourcePlugin(ABC, SourceExtraArgsClassBase):
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Fetches products from an external source.

        Returns:
            list[ProductDetails]: A list of products to be imported to the database
        """
        pass


class DocumentSourcePlugin(ABC, SourceExtraArgsClassBase):
    CONFIGURATION_ARGS = None

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[DocumentDetails]:
        """Fetches documents from an external system.

        Returns:
            list[DocumentDetails]: A list of documents to be imported to the database
        """
        pass


class LanguageModelProvider(ABC):
    STREAMING_AVAILABLE = True

    def __init__(self, model: str):
        super(LanguageModelProvider, self).__init__()
        self._model = model

    @abstractmethod
    def provide_language_model(self) -> BaseLanguageModel:
        """Initializes and returns an instance of the language model.

        Returns:
            An instance of the language model for the agent.
        """
        pass

    def provide_streaming_language_model(self, callbacks: list[BaseCallbackHandler] | None = None, **kwargs):
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
