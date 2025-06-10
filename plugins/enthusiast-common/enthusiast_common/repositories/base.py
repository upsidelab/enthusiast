from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, List


T = TypeVar("T")
U = TypeVar("U")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    @abstractmethod
    def get_by_id(self, pk: int) -> Optional[T]:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def create(self, **kwargs) -> T:
        pass

    @abstractmethod
    def update(self, pk: int, **kwargs) -> T:
        pass

    @abstractmethod
    def delete(self, pk: int) -> bool:
        pass


class BaseUserRepository(BaseRepository[T], ABC, Generic[T, U]):
    @abstractmethod
    def get_user_dataset(self, user_id: int, data_set_id: int) -> U:
        pass


class BaseMessageRepository(BaseRepository[T], ABC):
    pass


class BaseConversationRepository(BaseRepository[T], ABC):
    pass


class BaseDataSetRepository(BaseRepository[T], ABC):
    pass
