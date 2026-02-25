from django.conf import settings
from enthusiast_common.interfaces import ECommerceIntegrationPlugin

from sync.base import SourcePluginRegistry


class ECommerceIntegrationPluginRegistry(SourcePluginRegistry[ECommerceIntegrationPlugin]):
    """Registry of ecommerce integration plugins."""

    plugin_base = ECommerceIntegrationPlugin

    @staticmethod
    def _get_plugin_paths():
        return settings.CATALOG_ECOMMERCE_INTEGRATION_PLUGINS
