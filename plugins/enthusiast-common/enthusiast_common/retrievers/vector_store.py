from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

from ..registry import BaseEmbeddingProviderRegistry
from ..repositories import BaseDataSetRepository, BaseModelChunkRepository
from .base import BaseRetriever

T = TypeVar("T")


class BaseVectorStoreRetriever(BaseRetriever, ABC, Generic[T]):
    def __init__(
        self,
        data_set_id: int,
        data_set_repo: BaseDataSetRepository,
        model_chunk_repo: BaseModelChunkRepository[T],
        embeddings_registry: BaseEmbeddingProviderRegistry,
        max_objects: int = 12,
    ):
        self.data_set_id = data_set_id
        self.data_set_repo = data_set_repo
        self.embeddings_registry = embeddings_registry
        self.max_objects = max_objects
        self.model_chunk_repo = model_chunk_repo

    @abstractmethod
    def find_content_matching_query(self, query: str) -> Iterable[T]:
        pass
