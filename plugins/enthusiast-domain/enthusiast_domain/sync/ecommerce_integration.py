from enthusiast_domain_common.interfaces import ECommerceIntegrationPlugin
from enthusiast_domain_common.interfaces.integration_managers import BaseECommerceIntegrationManager

from enthusiast_domain.sync.product import ProductSourceManager


class ECommerceIntegrationManager(BaseECommerceIntegrationManager):
    """Syncs products from an ECommerceIntegrationPlugin by delegating to its product source."""

    def sync(self, plugin: ECommerceIntegrationPlugin, dataset_id: int, integration_id: int) -> None:
        source = plugin.build_product_source()
        ProductSourceManager(self._indexer).sync(source, dataset_id, integration_id)
