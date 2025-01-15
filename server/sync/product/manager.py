from enthusiast_common import ProductDetails

from catalog.models import Product, ProductSource
from sync.base import DataSetSource, SyncManager
from sync.product.registry import ProductSourcePluginRegistry


class ProductSyncManager(SyncManager[ProductDetails]):
    """Orchestrates synchronisation activities of registered product plugins."""

    def _build_registry(self):
        return ProductSourcePluginRegistry()

    def _get_all_sources(self) -> list[DataSetSource]:
        all_sources = [DataSetSource(plugin_name=source.plugin_name,
                                     data_set_id=source.data_set_id,
                                     config=source.config)
                       for source in ProductSource.objects.all()]
        return all_sources

    def _get_data_set_sources(self, data_set_id: int) -> list[DataSetSource]:
        data_set_sources = [DataSetSource(plugin_name=source.plugin_name,
                                          data_set_id=source.data_set_id,
                                          config=source.config)
                            for source in ProductSource.objects.filter(data_set_id=data_set_id)]
        return data_set_sources

    def _get_data_set_source(self, source_id: int) -> DataSetSource:
        source = ProductSource.objects.get(id=source_id)
        return DataSetSource(plugin_name=source.plugin_name,
                             data_set_id=source.data_set_id,
                             config=source.config)

    def _sync_item(self, data_set_id: int, item_data: ProductDetails):
        """Creates a product in the database.

        Args:
            data_set_id (int): obligatory, a data set to which imported data belongs to.
            item_data (dict): item details.
        """
        item, created = Product.objects.update_or_create(
            data_set_id=data_set_id,
            entry_id=item_data.entry_id,
            defaults={
                "name": item_data.name,
                "slug": item_data.slug,
                "description": item_data.description,
                "sku": item_data.sku,
                "properties": item_data.properties,
                "categories": item_data.categories,
                "price": item_data.price,
            }
        )

