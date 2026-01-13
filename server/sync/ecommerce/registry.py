import inspect
from importlib import import_module
from typing import Type

from django.conf import settings

from enthusiast_common.interfaces import ECommerceIntegrationPlugin

class ECommerceIntegrationPluginRegistry:
    """Registry of ecommerce integration plugins."""

    def get_plugin_paths(self) -> list[str]:
        return settings.CATALOG_ECOMMERCE_INTEGRATION_PLUGINS

    def get_plugin_class_by_path(self, path: str) -> Type[ECommerceIntegrationPlugin]:
        module_path, plugin_name = path.rsplit(".", 1)
        try:
            plugin_module = import_module(module_path)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Cannot import module '{module_path}'.") from e
        plugins = [
            cls_name
            for cls_name, cls in inspect.getmembers(plugin_module, inspect.isclass)
            if issubclass(cls, ECommerceIntegrationPlugin) and cls_name == plugin_name
        ]
        if not plugins:
            raise ValueError(f"No valid plugin classes found in module '{module_path}'.")
        return getattr(plugin_module, plugins[0])

