from pgvector.django import CosineDistance

from catalog.embeddings import EmbeddingProviderRegistry
from catalog.models import DocumentChunk, DataSet


class DocumentRetriever:
    def __init__(self, data_set: DataSet, max_documents: int = 12):
        self.data_set = data_set
        self.max_documents = max_documents

    def find_documents_matching_query(self, query: str) -> list[DocumentChunk]:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_documents = self._find_documents_matching_vector(embedding_vector)
        return relevant_documents

    def _create_embedding_for_query(self, query: str) -> list[float]:
        embedding_provider = EmbeddingProviderRegistry().provider_for_dataset(self.data_set)
        return embedding_provider.generate_embeddings(query)

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> list[DocumentChunk]:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_by_distance = DocumentChunk.objects.annotate(distance=embedding_distance).order_by("distance")
        embeddings_with_documents = embeddings_by_distance.select_related("document").filter(
            document__data_set_id__exact=self.data_set.id
        )
        limited_embeddings_with_documents = embeddings_with_documents[: self.max_documents]

        return limited_embeddings_with_documents
