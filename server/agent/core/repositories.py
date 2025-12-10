import json
from collections import defaultdict
from typing import Any, DefaultDict, Optional, Type, TypeVar

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models
from django.db.models import Q, QuerySet
from enthusiast_common.repositories import (
    BaseAgentRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseRepository,
    BaseUserRepository,
)
from enthusiast_common.structures import LLMFile
from pgvector.django import CosineDistance

from account.models import User
from agent.models import Conversation, Message
from agent.models.agent import Agent
from agent.models.conversation import ConversationFile
from catalog.models import DataSet, DocumentChunk, Product, ProductContentChunk

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


class DjangoProductChunkRepository(
    BaseDjangoRepository[ProductContentChunk], BaseModelChunkRepository[ProductContentChunk]
):
    def get_chunk_by_distance_for_data_set(
        self, data_set_id: int, distance: CosineDistance
    ) -> QuerySet[ProductContentChunk]:
        embeddings_by_distance = self.model.objects.annotate(distance=distance).order_by("distance")
        embeddings_with_products = embeddings_by_distance.select_related("product").filter(
            product__data_set_id__exact=data_set_id
        )
        return embeddings_with_products

    def get_chunk_by_distance_and_keyword_for_data_set(
        self, data_set_id: int, distance: CosineDistance, keyword: str
    ) -> QuerySet[ProductContentChunk]:
        embeddings_by_distance_and_keyword = (
            self.model.objects.annotate(
                rank=SearchRank(SearchVector("content"), SearchQuery(keyword)), distance=distance
            )
            .filter(rank__gt=0.05)
            .order_by("distance")
        )
        embeddings_with_products = embeddings_by_distance_and_keyword.select_related("product").filter(
            product__data_set_id__exact=data_set_id
        )
        return embeddings_with_products


class DjangoProductRepository(BaseDjangoRepository[Product], BaseProductRepository[Product]):
    def extra(self, where_conditions: list[str]) -> QuerySet[Product]:
        return self.model.objects.extra(where=where_conditions)

    def search_for_data_set_products(
        self, data_set_id: Any, filter_arguments: Q, exclude_arguments: Q, order_by_arguments: list[str] | None = None
    ) -> QuerySet[T]:
        query = self.model.objects.filter(data_set_id=data_set_id)
        if filter_arguments:
            query = query.filter(filter_arguments)
        if exclude_arguments:
            query = query.exclude(exclude_arguments)
        if order_by_arguments:
            query = query.order_by(*order_by_arguments)
        return query

    def describe_filtering_columns_for_llm(self) -> str:
        results = {}
        qs = self.model.objects.values_list("categories", "properties")
        categories_list = [row[0] for row in qs if row[0]]
        properties_list = [row[1] for row in qs if row[1]]

        results["categories"] = self._get_distinct_categories(categories_list)
        results["properties"] = self._get_distinct_properties(properties_list)

        return json.dumps(results)

    def _get_distinct_categories(self, unique_categories: list[list[str]]) -> list[str]:
        flat = [item for sublist in unique_categories if sublist for item in sublist]
        return list(set(flat))

    def _get_distinct_properties(self, unique_records: list[dict[str, str]]) -> dict[str, list[str]]:
        """
        Collect unique values for each key across all JSONField entries.
        """
        unique_properties: DefaultDict[str, set[str]] = defaultdict(set)

        for record in unique_records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if value is not None:
                        unique_properties[key].add(str(value))
        return {key: sorted(list(value)) for key, value in unique_properties.items()}


class DjangoMessageRepository(BaseDjangoRepository[Message], BaseMessageRepository[Message]):
    pass


class DjangoConversationRepository(BaseDjangoRepository[Conversation], BaseConversationRepository[Conversation]):
    def get_data_set_id(self, conversation_id: int) -> int:
        return self.get_by_id(pk=conversation_id).data_set.id

    def get_agent_id(self, conversation_id: int) -> int:
        return self.get_by_id(pk=conversation_id).agent.id

    def list_files(self, conversation_id: int) -> list[LLMFile]:
        return [file.get_llm_file_object() for file in self.get_by_id(pk=conversation_id).files.filter(is_hidden=False)]

    def get_file_objects(self, conversation_id: Any, file_ids: list[Any]) -> list[LLMFile]:
        return [
            file.get_llm_file_object()
            for file in ConversationFile.objects.filter(
                conversation_id=conversation_id, id__in=file_ids, is_hidden=False
            ).order_by("created_at")
        ]


class DjangoDataSetRepository(BaseDjangoRepository[DataSet], BaseDataSetRepository[DataSet]):
    pass


class DjangoAgentRepository(BaseDjangoRepository[Agent], BaseAgentRepository[Agent]):
    def get_agent_configuration_by_id(self, agent_id: int) -> Any:
        return self.get_by_id(agent_id).config
