from enthusiast_common import EmbeddingProvider
from ollama import Client


class OllamaEmbeddingProvider(EmbeddingProvider):
    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using Ollama's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        embedding_response = Client().embed(self._model, input=content)

        return list(embedding_response.embeddings[0])

    @staticmethod
    def available_models() -> list[str]:
        all_models = Client().list().models
        embedding_models = [model.name for model in all_models if model.name.contains("embed")]
        return embedding_models
