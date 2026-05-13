from enthusiast_common.registry.embeddings import EmbeddingProvider
from ollama import Client


class OllamaEmbeddingProvider(EmbeddingProvider):
    NAME = "Ollama"

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
        all_model_names = [m.model for m in Client().list().models]
        embedding_models = [
            model_name for model_name in all_model_names
                        if model_name and OllamaEmbeddingProvider.is_embedding_model(model_name)
        ]
        return embedding_models


    @staticmethod
    def is_embedding_model(model_name: str) -> bool:
        return 'embed' in model_name
