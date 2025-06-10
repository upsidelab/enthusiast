from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Type, TypeVar, Generic

from django.conf import settings
from django.db import models


T = TypeVar("T")


class BaseDBModelsRegistry(ABC, Generic[T]):
    def __init__(self, models_config: dict[Any, Any]):
        self._models_config = models_config

    @abstractmethod
    def get_model_class_by_name(self, name: str) -> Type[T]:
        pass


class BaseDjangoSettingsDBModelRegistry(BaseDBModelsRegistry[models.Model]):
    def __init__(self):
        models_config = settings.CATALOG_MODELS
        super().__init__(models_config)
        self.models_config = models_config

    def get_model_class_by_name(self, name: str) -> Type[models.Model]:
        try:
            model_class_path = self.models_config[name]
        except KeyError:
            raise ValueError(f"Model '{name}' is not defined in settings.CATALOG_MODELS.")

        try:
            module_name, class_name = model_class_path.rsplit(".", 1)
        except ValueError:
            raise ValueError(f"Invalid model path format for '{name}': '{model_class_path}'")

        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            raise ImportError(f"Cannot import module '{module_name}' for model '{name}'.")

        try:
            model_class = getattr(module, class_name)
        except AttributeError:
            raise ImportError(f"Module '{module_name}' has no attribute '{class_name}' for model '{name}'.")

        if not issubclass(model_class, models.Model):
            raise TypeError(
                f"Resolved class '{model_class}' for model '{name}' is not a subclass of django.db.models.Model"
            )
        return model_class
