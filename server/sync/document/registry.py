from typing import Type

from django.conf import settings
from enthusiast_common import DocumentSourcePlugin

from sync.base import SourcePluginRegistry
from utils.base_registry import BaseRegistry


class DocumentSourcePluginRegistry(SourcePluginRegistry, BaseRegistry[DocumentSourcePlugin]):
    """Registry of document source plugins."""

    plugin_base = DocumentSourcePlugin

    def get_plugins(self):
        return settings.CATALOG_DOCUMENT_SOURCE_PLUGINS.items()

    def get_plugin_class_by_name(self, name: str) -> Type[DocumentSourcePlugin]:
        path = settings.CATALOG_DOCUMENT_SOURCE_PLUGINS[name]
        return self._get_plugin_class_by_path(path)