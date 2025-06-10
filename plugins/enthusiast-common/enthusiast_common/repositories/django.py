from typing import TypeVar, Type, Optional, Generic

from django.db import models


from .base import (
    BaseRepository,
    BaseMessageRepository,
    BaseConversationRepository,
    BaseUserRepository,
    BaseDataSetRepository,
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


class DjangoMessageRepository(
    BaseDjangoRepository[T], BaseMessageRepository, Generic[T]
):
    pass


class DjangoConversationRepository(
    BaseDjangoRepository[T], BaseConversationRepository, Generic[T]
):
    pass


class DjangoDataSetRepository(
    BaseDjangoRepository[T], BaseDataSetRepository, Generic[T]
):
    pass
