from abc import ABC, abstractmethod
from typing import Any, Type


class EmbeddingProvider(ABC):
    """Base class for embedding providers.

    Subclasses must set the ``NAME`` class attribute to a human-readable
    provider name (e.g. ``"OpenAI"``).  This value is used for display
    in the UI and for looking up the provider in the registry.
    """

    NAME: str = None

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
    """Registry of available embedding providers.

    Subclasses must implement ``_get_plugin_paths`` to return the list of
    class paths from settings and ``provider_for_dataset`` to resolve a
    provider for a given data set.
    """

    @abstractmethod
    def get_provider_classes(self) -> list[Type[EmbeddingProvider]]:
        """Returns all registered provider classes."""

    @abstractmethod
    def provider_class_by_name(self, name: str) -> Type[EmbeddingProvider]:
        """Looks up a provider class by its ``NAME`` attribute."""

    @abstractmethod
    def provider_for_dataset(self, data_set_id: Any) -> Type[EmbeddingProvider]:
        """Returns the provider class configured for the given data set."""
