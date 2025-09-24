import inspect
from importlib import import_module
from typing import Type

from django.conf import settings
from enthusiast_common import ProductSourcePlugin

from sync.base import SourcePluginRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry):
    """Registry of product sync plugins."""

    def get_plugins(self):
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()

    def get_plugin_class_by_name(self, name: str) -> Type[ProductSourcePlugin]:
        path = settings.CATALOG_PRODUCT_SOURCE_PLUGINS[name]
        module_path, plugin_name = path.rsplit(".", 1)
        try:
            plugin_module = import_module(module_path)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Cannot import module '{module_path}'.") from e
        plugins = [
            cls_name
            for cls_name, cls in inspect.getmembers(plugin_module, inspect.isclass)
            if issubclass(cls, ProductSourcePlugin) and cls_name == plugin_name
        ]
        if not plugins:
            raise ValueError(f"No valid plugin classes found in module '{module_path}'.")
        return getattr(plugin_module, plugins[0])
