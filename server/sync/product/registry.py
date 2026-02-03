from typing import Type

from django.conf import settings
from enthusiast_common import ProductSourcePlugin

from sync.base import SourcePluginRegistry
from utils.base_registry import BaseRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry, BaseRegistry[ProductSourcePlugin]):
    """Registry of product sync plugins."""
    plugin_base = ProductSourcePlugin

    def get_plugins(self):
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()

    def get_plugin_class_by_name(self, name: str) -> Type[ProductSourcePlugin]:
        path = settings.CATALOG_PRODUCT_SOURCE_PLUGINS[name]
        return self._get_plugin_class_by_path(path)