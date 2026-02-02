import inspect
from abc import ABC, abstractmethod
from importlib import import_module
from typing import Type, Generic, TypeVar, List

T = TypeVar("T")

class BaseRegistry(ABC, Generic[T]):

    plugin_base: Type[T]

    @abstractmethod
    def get_plugin_paths(self) -> list[str]:
        pass

    def get_plugin_classes(self) -> List[Type[T]]:
        return [self.get_plugin_class_by_path(path) for path in self.get_plugin_paths()]

    def get_plugin_classes_by_names(self) -> dict[str, Type[T]]:
        return { plugin_class.NAME: plugin_class for plugin_class in self.get_plugin_classes() }

    def get_plugin_class_by_path(self, path: str) -> Type[T]:
        module_path, plugin_name = path.rsplit(".", 1)
        try:
            plugin_module = import_module(module_path)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Cannot import module '{module_path}'.") from e
        plugins = [
            cls_name
            for cls_name, cls in inspect.getmembers(plugin_module, inspect.isclass)
            if issubclass(cls, self.plugin_base) and cls_name == plugin_name
        ]
        if not plugins:
            raise ValueError(f"No valid plugin classes found in module '{module_path}'.")
        return getattr(plugin_module, plugins[0])