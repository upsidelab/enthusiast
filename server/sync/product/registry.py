from typing import Type

from django.conf import settings
from enthusiast_common import ProductSourcePlugin

from sync.base import SourcePluginRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry[ProductSourcePlugin]):
    """Registry of product sync plugins."""

    plugin_base = ProductSourcePlugin

    def get_plugin_names(self) -> list[str]:
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS.keys()

    def get_plugin_class_by_name(self, name: str) -> Type[ProductSourcePlugin]:
        path = settings.CATALOG_PRODUCT_SOURCE_PLUGINS[name]
        return self._get_plugin_class_by_path(path)
