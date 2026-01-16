import inspect
from importlib import import_module
from typing import Type

from django.conf import settings
from enthusiast_common.interfaces import ECommerceIntegrationPlugin

from catalog.models import ECommerceIntegration


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

    def get_plugin_classes_by_names(self) -> dict[str, Type[ECommerceIntegrationPlugin]]:
        plugin_classes = [self.get_plugin_class_by_path(path) for path in self.get_plugin_paths()]
        return { plugin_class.NAME: plugin_class for plugin_class in plugin_classes }

    def get_plugin_instance(self, ecommerce_integration: ECommerceIntegration) -> ECommerceIntegrationPlugin:
        plugin_classes_by_names = self.get_plugin_classes_by_names()
        plugin_class = plugin_classes_by_names[ecommerce_integration.plugin_name]
        plugin_instance = plugin_class(data_set_id=ecommerce_integration.data_set_id)
        plugin_instance.set_runtime_arguments(ecommerce_integration.config)
        return plugin_instance
