from django.db.models import QuerySet
from enthusiast_common.injectors import BaseDocumentRetriever
from pgvector.django import CosineDistance

from catalog.models import DocumentChunk


class DocumentRetriever(BaseDocumentRetriever[DocumentChunk]):
    def find_documents_matching_query(self, query: str) -> QuerySet[DocumentChunk]:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_documents = self._find_documents_matching_vector(embedding_vector)
        return relevant_documents

    def _create_embedding_for_query(self, query: str) -> list[float]:
        data_set = self.data_set_repo.get_by_id(self.data_set_id)
        embedding_provider = self.embeddings_registry.provider_for_dataset(self.data_set_id)
        return embedding_provider(data_set.embedding_model, data_set.embedding_vector_dimensions).generate_embeddings(
            query
        )

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> QuerySet[DocumentChunk]:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_with_documents = self.document_chunk_repo.get_document_chunk_by_distance_for_data_set(
            self.data_set_id, embedding_distance
        )
        limited_embeddings_with_documents = embeddings_with_documents[: self.max_documents]
        return limited_embeddings_with_documents
