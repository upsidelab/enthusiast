from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar

from pgvector.django import CosineDistance

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
    def filter(self, **kwargs) -> List[T]:
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
    def get_user_dataset(self, user_id: Any, data_set_id: Any) -> U:
        pass


class BaseModelChunkRepository(BaseRepository[T], ABC):
    def get_chunk_by_distance_for_data_set(self, data_set_id: Any, distance: CosineDistance) -> Optional[T]:
        pass


class BaseProductRepository(BaseRepository[T], ABC):
    @abstractmethod
    def extra(self, where_conditions: list[str]) -> list[T]:
        pass


class BaseMessageRepository(BaseRepository[T], ABC):
    pass


class BaseConversationRepository(BaseRepository[T], ABC):
    @abstractmethod
    def get_data_set_id(self, conversation_id: Any) -> Any:
        pass

    @abstractmethod
    def get_agent_id(self, conversation_id: Any) -> Any:
        pass

    @abstractmethod
    def list_files(self, conversation_id: Any) -> List[Any]:
        pass

    @abstractmethod
    def get_file_objects(self, conversation_id: Any, file_ids: list[Any]) -> List[Any]:
        pass


class BaseDataSetRepository(BaseRepository[T], ABC):
    pass


class BaseAgentRepository(BaseRepository[T], ABC):
    @abstractmethod
    def get_agent_configuration_by_id(self, conversation_id: Any) -> Any:
        pass
