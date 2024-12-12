from catalog.models import ProductSource
from django.conf import settings
from sync.base import DataSetPlugin, SourcePluginRegistry


class ProductSourcePluginRegistry(SourcePluginRegistry):
    """Registry of product sync plugins."""

    def get_plugins(self):
        return settings.CATALOG_PRODUCT_SOURCE_PLUGINS.items()

    def get_data_set_config(self, plugin_name):
        source = ProductSource.objects.get(plugin_name=plugin_name)
        return DataSetPlugin(data_set_id=source.data_set_id, config=source.config)

