import os

from enthusiast_common.registry.embeddings import EmbeddingProvider
from enthusiast_common.utils import prioritize_items
from mistralai import Mistral

PRIORITIZED_MODELS = ["mistral-embed"]

# These models produce a fixed-size output vector and do not accept the
# output_dimension parameter in the Mistral embeddings API.
FIXED_DIMENSION_MODELS: dict[str, list[int]] = {
    "mistral-embed": [1024],
    "mistral-embed-2312": [1024],
}


class MistralAIEmbeddingProvider(EmbeddingProvider):
    NAME = "Mistral AI"

    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using Mistral's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

        kwargs = {"inputs": content, "model": self._model}
        if self._model not in FIXED_DIMENSION_MODELS:
            kwargs["output_dimension"] = self._dimensions

        mistral_embedding = client.embeddings.create(**kwargs)

        return mistral_embedding.data[0].embedding

    @staticmethod
    def available_models() -> list[str]:
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        all_models = client.models.list().data
        embedding_models = [model.id for model in all_models if "embed" in model.id]
        return prioritize_items(embedding_models, PRIORITIZED_MODELS)

    @classmethod
    def vector_size_constraints(cls) -> dict[str, list[int]]:
        return FIXED_DIMENSION_MODELS
