from typing import List, Type

from django.conf import settings
from enthusiast_common.interfaces import ECommerceIntegrationPlugin

from sync.base import SourcePluginRegistry


class ECommerceIntegrationPluginRegistry(SourcePluginRegistry[ECommerceIntegrationPlugin]):
    """Registry of ecommerce integration plugins."""

    plugin_base = ECommerceIntegrationPlugin

    def get_plugin_classes(self) -> List[Type[ECommerceIntegrationPlugin]]:
        return [self._get_plugin_class_by_path(path) for path in self._get_plugin_paths()]

    @staticmethod
    def _get_plugin_paths() -> List[str]:
        return settings.CATALOG_ECOMMERCE_INTEGRATION_PLUGINS

    def _get_plugin_classes_by_names(self) -> dict[str, Type[ECommerceIntegrationPlugin]]:
        return {plugin_class.NAME: plugin_class for plugin_class in self.get_plugin_classes()}

    def get_plugin_class_by_name(self, name: str) -> Type[ECommerceIntegrationPlugin]:
        return self._get_plugin_classes_by_names()[name]

    def get_plugin_names(self) -> list[str]:
        return list(self._get_plugin_classes_by_names().keys())
