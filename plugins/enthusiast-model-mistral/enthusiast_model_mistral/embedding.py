import os

from enthusiast_common.registry.embeddings import EmbeddingProvider
from enthusiast_common.utils import prioritize_items
from mistralai import Mistral

PRIORITIZED_MODELS = ["mistral-embed"]


class MistralAIEmbeddingProvider(EmbeddingProvider):
    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using Mistral's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        mistral_embedding = client.embeddings.create(
            inputs=content, output_dimension=self._dimensions, model=self._model
        )

        return mistral_embedding.data[0].embedding

    @staticmethod
    def available_models() -> list[str]:
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        all_models = client.models.list().data
        embedding_models = [model.id for model in all_models if "embed" in model.id]
        return prioritize_items(embedding_models, PRIORITIZED_MODELS)
