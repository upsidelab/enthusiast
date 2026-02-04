import inspect
from abc import ABC
from importlib import import_module
from typing import Generic, Type, TypeVar

T = TypeVar("T")
U = TypeVar("U")

class BaseRegistry(ABC, Generic[T]):
    plugin_base: Type[T]

    def _get_plugin_class_by_path(self, path: str) -> Type[T]:
        return self._get_class_by_path(path, self.plugin_base)

    @staticmethod
    def _get_class_by_path(path: str, base_class: Type[U]) -> Type[U]:
        module_path, plugin_name = path.rsplit(".", 1)
        try:
            plugin_module = import_module(module_path)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Cannot import module '{module_path}'.") from e
        plugins = [
            cls_name
            for cls_name, cls in inspect.getmembers(plugin_module, inspect.isclass)
            if issubclass(cls, base_class) and cls_name == plugin_name
        ]
        if not plugins:
            raise ValueError(f"No valid plugin classes found in module '{module_path}'.")
        return getattr(plugin_module, plugins[0])
