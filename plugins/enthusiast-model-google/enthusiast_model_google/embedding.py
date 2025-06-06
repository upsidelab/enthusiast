from enthusiast_common import EmbeddingProvider
from enthusiast_common.utils import prioritize_items
from google import genai
from google.genai.types import EmbedContentConfig


PRIORITIZED_MODELS = ["models/embedding-001", "models/text-embedding-004"]


class GoogleEmbeddingProvider(EmbeddingProvider):
    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using OpenAI's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        config = EmbedContentConfig(output_dimensionality=self._dimensions)
        google_embedding = genai.Client().models.embed_content(
            model=self._model,
            config=config,
            contents=content,
        )

        return google_embedding.embeddings[0].values

    @staticmethod
    def available_models() -> list[str]:
        all_models = genai.Client().models.list()
        embedding_models = [model.name for model in all_models if "embedContent" in model.supported_actions]
        return prioritize_items(embedding_models, PRIORITIZED_MODELS)
