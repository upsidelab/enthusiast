from django.conf import settings
from enthusiast_common import ProductSourcePlugin

from sync.base import SourcePluginRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry[ProductSourcePlugin]):
    """Registry of product sync plugins."""

    plugin_base = ProductSourcePlugin

    @staticmethod
    def _get_plugin_paths():
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS
