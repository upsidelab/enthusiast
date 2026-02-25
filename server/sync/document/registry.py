from django.conf import settings
from enthusiast_common import DocumentSourcePlugin

from sync.base import SourcePluginRegistry


class DocumentSourcePluginRegistry(SourcePluginRegistry[DocumentSourcePlugin]):
    """Registry of document source plugins."""

    plugin_base = DocumentSourcePlugin

    @staticmethod
    def _get_plugin_paths():
        return settings.CATALOG_DOCUMENT_SOURCE_PLUGINS
