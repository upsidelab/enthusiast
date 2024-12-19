from django.conf import settings
from sync.base import SourcePluginRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry):
    """Registry of product sync plugins."""

    def get_plugins(self):
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()
