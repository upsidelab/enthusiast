from openai import OpenAI

from catalog.embeddings.embedding_provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def generate_embeddings(self, content: str) -> list[float]:
        """
        Generates and returns an embedding vector for the given content using OpenAI's embeddings API.

        Args:
            content (str): The input text for which the embedding vector is to be generated.
        """
        client = OpenAI()

        openai_embedding = client.embeddings.create(model=self._model,
                                                    dimensions=self._dimensions,
                                                    input=content)

        return openai_embedding.data[0].embedding
