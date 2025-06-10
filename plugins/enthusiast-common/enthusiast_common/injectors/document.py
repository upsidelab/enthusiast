from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

from django.db.models import QuerySet
from pgvector.django import CosineDistance

from ..registry import BaseEmbeddingProviderRegistry
from ..repositories import BaseDataSetRepository
from ..repositories import BaseDocumentChunkRepository


T = TypeVar("T")


class BaseDocumentRetriever(ABC, Generic[T]):
    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        document_chunk_repo: BaseDocumentChunkRepository,
        embeddings_registry: BaseEmbeddingProviderRegistry,
        max_documents: int = 12,
    ):
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.embeddings_registry = embeddings_registry
        self.max_documents = max_documents
        self.document_chunk_repo = document_chunk_repo

    @abstractmethod
    def find_documents_matching_query(self, query: str) -> Iterable[T]:
        pass

    def _create_embedding_for_query(self, query: str) -> list[float]:
        pass

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> Iterable[T]:
        pass


class DjangoDocumentRetriever(BaseDocumentRetriever[T], Generic[T]):
    def find_documents_matching_query(self, query: str) -> QuerySet[T]:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_documents = self._find_documents_matching_vector(embedding_vector)
        return relevant_documents

    def _create_embedding_for_query(self, query: str) -> list[float]:
        data_set = self.data_set_repo.get_by_id(self.data_set_id)
        embedding_provider = self.embeddings_registry.provider_for_dataset(self.data_set_id)
        return embedding_provider(data_set.embedding_model, data_set.embedding_vector_dimensions).generate_embeddings(
            query
        )

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> QuerySet[T]:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_with_documents = self.document_chunk_repo.get_document_chunk_by_distance_for_data_set(
            self.data_set_id, embedding_distance
        )
        limited_embeddings_with_documents = embeddings_with_documents[: self.max_documents]
        return limited_embeddings_with_documents
