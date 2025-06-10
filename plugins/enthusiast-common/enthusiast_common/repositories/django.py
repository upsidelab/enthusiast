from typing import TypeVar, Type, Optional, Generic

from django.db import models
from django.db.models import QuerySet
from pgvector.django import CosineDistance

from .base import (
    BaseRepository,
    BaseMessageRepository,
    BaseConversationRepository,
    BaseUserRepository,
    BaseDataSetRepository,
    BaseDocumentChunkRepository,
    BaseProductRepository,
)

T = TypeVar("T", bound=models.Model)
U = TypeVar("U", bound=models.Model)


class BaseDjangoRepository(BaseRepository[T]):
    def __init__(self, model: Type[T]):
        super(BaseDjangoRepository, self).__init__(model)
        self.model = model

    def get_by_id(self, pk: int) -> Optional[T]:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def list(self) -> list[T]:
        return list(self.model.objects.all())

    def filter(self, **kwargs) -> QuerySet[T]:
        return self.model.objects.filter(**kwargs)

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        instance.save()
        return instance

    def update(self, pk: int, **kwargs) -> Optional[T]:
        obj = self.get_by_id(pk)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    def delete(self, pk: int) -> bool:
        deleted, _ = self.model.objects.filter(pk=pk).delete()
        return deleted > 0


class DjangoUserRepository(BaseDjangoRepository[T], BaseUserRepository, Generic[T, U]):
    def get_user_dataset(self, user_id: int, data_set_id: int) -> U:
        user = self.model.objects.get(pk=user_id)
        return user.datasets.get(pk=data_set_id)


class DjangoDocumentChunkRepository(BaseDjangoRepository[T], BaseDocumentChunkRepository, Generic[T]):
    def get_document_chunk_by_distance_for_data_set(self, data_set_id: int, distance: CosineDistance) -> QuerySet[T]:
        embeddings_by_distance = self.model.objects.annotate(distance=distance).order_by("distance")
        embeddings_with_documents = embeddings_by_distance.select_related("document").filter(
            document__data_set_id__exact=data_set_id
        )
        return embeddings_with_documents


class DjangoProductRepository(BaseDjangoRepository[T], BaseProductRepository[T], Generic[T]):
    def extra(self, where_conditions: list[str]) -> QuerySet[T]:
        return self.model.objects.extra(where=where_conditions)


class DjangoMessageRepository(BaseDjangoRepository[T], BaseMessageRepository, Generic[T]):
    pass


class DjangoConversationRepository(BaseDjangoRepository[T], BaseConversationRepository, Generic[T]):
    def get_data_set_id(self, conversation_id: int) -> int:
        return self.get_by_id(pk=conversation_id).data_set.id


class DjangoDataSetRepository(BaseDjangoRepository[T], BaseDataSetRepository, Generic[T]):
    pass
