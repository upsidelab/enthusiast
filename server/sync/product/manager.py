from catalog.models import Product
from sync.base import SyncManager
from common.plugin.interface import ItemData
from sync.product.registry import ProductSourcePluginRegistry


class ProductSyncManager(SyncManager):
    """Orchestrates synchronisation activities of registered product plugins."""

    def _build_registry(self):
        return ProductSourcePluginRegistry()

    def _sync_item(self, data_set_id: int, item_data: ItemData):
        """Creates a product in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (dict): item details.
        """
        item, created = Product.objects.update_or_create(
            entry_id=item_data.entry_id,
            defaults={
                "data_set_id": data_set_id,
                "name": item_data.name,
                "slug": item_data.slug,
                "description": item_data.description,
                "sku": item_data.sku,
                "properties": item_data.properties,
                "categories": item_data.categories,
                "price": item_data.price,
            }
        )

