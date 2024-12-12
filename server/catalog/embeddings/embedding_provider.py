from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    def __init__(self, model, dimensions):
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
