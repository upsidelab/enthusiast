from typing import List, Type

from django.conf import settings
from enthusiast_common.interfaces import ECommerceIntegrationPlugin
from utils.base_registry import BaseRegistry

from catalog.models import ECommerceIntegration


class ECommerceIntegrationPluginRegistry(BaseRegistry[ECommerceIntegrationPlugin]):
    """Registry of ecommerce integration plugins."""

    plugin_base = ECommerceIntegrationPlugin

    def get_plugin_instance(self, ecommerce_integration: ECommerceIntegration) -> ECommerceIntegrationPlugin:
        plugin_classes_by_names = self._get_plugin_classes_by_names()
        plugin_class = plugin_classes_by_names[ecommerce_integration.plugin_name]
        plugin_instance = plugin_class(data_set_id=ecommerce_integration.data_set_id)
        plugin_instance.set_runtime_arguments(ecommerce_integration.config)
        return plugin_instance

    def get_plugin_classes(self) -> List[Type[ECommerceIntegrationPlugin]]:
        return [self._get_plugin_class_by_path(path) for path in self._get_plugin_paths()]

    @staticmethod
    def _get_plugin_paths() -> List[str]:
        return settings.CATALOG_ECOMMERCE_INTEGRATION_PLUGINS

    def _get_plugin_classes_by_names(self) -> dict[str, Type[ECommerceIntegrationPlugin]]:
        return { plugin_class.NAME: plugin_class for plugin_class in self.get_plugin_classes() }
