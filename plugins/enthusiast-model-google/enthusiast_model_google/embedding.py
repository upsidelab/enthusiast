from enthusiast_common.registry.embeddings import EmbeddingProvider
from enthusiast_common.utils import prioritize_items
from google import genai
from google.genai.types import EmbedContentConfig

PRIORITIZED_MODELS = ["models/embedding-001", "models/text-embedding-004"]


class GoogleEmbeddingProvider(EmbeddingProvider):
    NAME = "Google"

    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using OpenAI's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        config = EmbedContentConfig(output_dimensionality=self._dimensions)
        with genai.Client() as client:
            google_embedding = client.models.embed_content(
                model=self._model,
                config=config,
                contents=content,
            )

        return google_embedding.embeddings[0].values

    @staticmethod
    def available_models() -> list[str]:
        with genai.Client() as client:
            all_models = client.models.list()

        embedding_models = [model.name for model in all_models if "embedContent" in model.supported_actions]
        return prioritize_items(embedding_models, PRIORITIZED_MODELS)
