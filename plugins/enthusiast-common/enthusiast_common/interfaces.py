from abc import ABC, abstractmethod

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Type, Optional

from enthusiast_common.structures import ProductDetails, DocumentDetails


class ProductSourcePlugin(ABC):
    def __init__(self, data_set_id, config: dict):
        self.config = config
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Fetches products from an external source.

        Returns:
            list[ProductDetails]: A list of products to be imported to the database
        """
        pass


class DocumentSourcePlugin(ABC):
    def __init__(self, data_set_id, config: dict):
        self.config = config
        self.data_set_id = data_set_id

    @abstractmethod
    def fetch(self) -> list[DocumentDetails]:
        """Fetches documents from an external system.

        Returns:
            list[DocumentDetails]: A list of documents to be imported to the database
        """
        pass


class LanguageModelProvider(ABC):
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


class CustomTool(BaseTool):
    name: str
    description: str
    args_schema: Type[BaseModel]
    return_direct: bool
    data_set: any # TODO use a proper type definition
    chat_model: Optional[str]

    def __init__(self, data_set, chat_model, language_model_provider: LanguageModelProvider, **kwargs):
        """Initialize the ToolInterface.

        Args:
            data_set (Any): The dataset used by the tool.
            chat_model (str, deprecated): This param is deprecated and will be removed in future versions. Use `language_model_provider.model_name()` instead.
            language_model_provider (LanguageModelProvider): A language model provider that the tool can use.
            **kwargs: Additional keyword arguments.
        """
        super(CustomTool, self).__init__(**kwargs)
        self.data_set = data_set
        self.chat_model = chat_model
        self._language_model_provider = language_model_provider

    @abstractmethod
    def _run(self, *args, **kwargs):
        """ Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass