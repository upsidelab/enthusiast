from typing import Optional, Type, TypeVar

from django.db import models
from django.db.models import QuerySet
from enthusiast_common.repositories import (
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseRepository,
    BaseUserRepository,
)
from pgvector.django import CosineDistance

from account.models import User
from agent.models import Conversation, Message
from catalog.models import DataSet, DocumentChunk, Product, ProductChunk

T = TypeVar("T", bound=models.Model)


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


class DjangoUserRepository(
    BaseDjangoRepository[User],
    BaseUserRepository,
):
    def get_user_dataset(self, user_id: int, data_set_id: int) -> DataSet:
        user = self.model.objects.get(pk=user_id)
        return user.datasets.get(pk=data_set_id)


class DjangoDocumentChunkRepository(BaseDjangoRepository[DocumentChunk], BaseModelChunkRepository[DocumentChunk]):
    def get_chunk_by_distance_for_data_set(self, data_set_id: int, distance: CosineDistance) -> QuerySet[DocumentChunk]:
        embeddings_by_distance = self.model.objects.annotate(distance=distance).order_by("distance")
        embeddings_with_documents = embeddings_by_distance.select_related("document").filter(
            document__data_set_id__exact=data_set_id
        )
        return embeddings_with_documents


class DjangoProductChunkRepository(BaseDjangoRepository[ProductChunk], BaseModelChunkRepository[ProductChunk]):
    def get_chunk_by_distance_for_data_set(self, data_set_id: int, distance: CosineDistance) -> QuerySet[ProductChunk]:
        embeddings_by_distance = self.model.objects.annotate(distance=distance).order_by("distance")
        embeddings_with_products = embeddings_by_distance.select_related("product").filter(
            product__data_set_id__exact=data_set_id
        )
        return embeddings_with_products


class DjangoProductRepository(BaseDjangoRepository[Product], BaseProductRepository[Product]):
    def extra(self, where_conditions: list[str]) -> QuerySet[Product]:
        return self.model.objects.extra(where=where_conditions)


class DjangoMessageRepository(BaseDjangoRepository[Message], BaseMessageRepository[Message]):
    pass


class DjangoConversationRepository(BaseDjangoRepository[Conversation], BaseConversationRepository[Conversation]):
    def get_data_set_id(self, conversation_id: int) -> int:
        return self.get_by_id(pk=conversation_id).data_set.id


class DjangoDataSetRepository(BaseDjangoRepository[DataSet], BaseDataSetRepository[DataSet]):
    pass
