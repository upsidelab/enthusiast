from typing import Type

from django.conf import settings
from enthusiast_common.interfaces import ECommerceIntegrationPlugin

from catalog.models import ECommerceIntegration
from utils.base_registry import BaseRegistry


class ECommerceIntegrationPluginRegistry(BaseRegistry[ECommerceIntegrationPlugin]):
    """Registry of ecommerce integration plugins."""

    plugin_base = ECommerceIntegrationPlugin

    def get_plugin_paths(self) -> list[str]:
        return settings.CATALOG_ECOMMERCE_INTEGRATION_PLUGINS

    def get_plugin_instance(self, ecommerce_integration: ECommerceIntegration) -> ECommerceIntegrationPlugin:
        plugin_classes_by_names = self.get_plugin_classes_by_names()
        plugin_class = plugin_classes_by_names[ecommerce_integration.plugin_name]
        plugin_instance = plugin_class(data_set_id=ecommerce_integration.data_set_id)
        plugin_instance.set_runtime_arguments(ecommerce_integration.config)
        return plugin_instance
