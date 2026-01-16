from enthusiast_common import ProductDetails

from catalog.models import Product, ProductSource, ECommerceIntegration
from catalog.tasks import index_product_task
from sync.base import DataSetSource, SyncManager
from sync.ecommerce.registry import ECommerceIntegrationPluginRegistry
from sync.product.registry import ProductSourcePluginRegistry


class ECommerceSyncManager:
    """Orchestrates synchronisation activities of registered product plugins."""

    def sync(self, source_id: int):
        integration = ECommerceIntegration.objects.get(id=source_id)
        plugin = self._build_registry().get_plugin_instance(integration)
        product_source = plugin.build_product_source()

        for product_data in product_source.fetch():
            self._sync_item(data_set_id=plugin.data_set_id, product_data=product_data)

    def _build_registry(self):
        return ECommerceIntegrationPluginRegistry()

    def _sync_item(self, data_set_id: int, product_data: ProductDetails):
        """Creates a product in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            product_data (dict): item details.
        """
        item, created = Product.objects.update_or_create(
            data_set_id=data_set_id,
            entry_id=product_data.entry_id,
            defaults={
                "name": product_data.name,
                "slug": product_data.slug,
                "description": product_data.description,
                "sku": product_data.sku,
                "properties": product_data.properties,
                "categories": product_data.categories,
                "price": product_data.price,
            },
        )
        index_product_task.apply_async([item.id])
