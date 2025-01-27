from abc import ABC, abstractmethod

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Type, Any

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

    def __init__(self, data_set, chat_model, **kwargs):
        """Initialize the ToolInterface.

        Args:
            data_set (Any): The dataset used by the tool.
            chat_model (str): The chat model used by the tool.
            **kwargs: Additional keyword arguments.
        """
        super(CustomTool, self).__init__(**kwargs)
        self.data_set = data_set
        self.chat_model = chat_model

    @abstractmethod
    def _run(self, *args, **kwargs):
        """ Abstract method to run the tool.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass