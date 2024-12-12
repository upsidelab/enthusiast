from django.conf import settings
from catalog.models import DocumentSource
from sync.base import DataSetPlugin, SourcePluginRegistry


class DocumentSourcePluginRegistry(SourcePluginRegistry):
    """Registry of document source plugins."""

    def get_plugins(self):
        return settings.CATALOG_DOCUMENT_SOURCE_PLUGINS.items()

    def get_data_set_config(self, plugin_name):
        source = DocumentSource.objects.get(plugin_name=plugin_name)
        return DataSetPlugin(data_set_id=source.data_set_id, config=source.config)
