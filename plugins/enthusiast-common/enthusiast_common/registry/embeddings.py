from abc import ABC, abstractmethod
from typing import Any, Type


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


class BaseEmbeddingProviderRegistry(ABC):
    def __init__(self, providers: dict[Any, Any]):
        self._providers = providers

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        pass

    @abstractmethod
    def provider_for_dataset(self, data_set_id: Any) -> Type[EmbeddingProvider]:
        pass
