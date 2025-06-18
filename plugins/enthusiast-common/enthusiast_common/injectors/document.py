from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

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
