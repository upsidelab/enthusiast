from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

T = TypeVar("T")


class BaseDBModelsRegistry(ABC, Generic[T]):
    def __init__(self, models_config: dict[Any, Any]):
        self._models_config = models_config

    @abstractmethod
    def get_model_class_by_name(self, name: str) -> Type[T]:
        pass
