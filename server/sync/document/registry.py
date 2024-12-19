from django.conf import settings
from sync.base import SourcePluginRegistry


class DocumentSourcePluginRegistry(SourcePluginRegistry):
    """Registry of document source plugins."""

    def get_plugins(self):
        return settings.CATALOG_DOCUMENT_SOURCE_PLUGINS.items()

