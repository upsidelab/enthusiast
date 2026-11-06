from typing import Any

from enthusiast_domain_common import ProductSourcePlugin
from enthusiast_domain_common.interfaces.integration_managers import BaseProductSourceManager

from enthusiast_domain.models import Product


class ProductSourceManager(BaseProductSourceManager):
    """Syncs products from a ProductSourcePlugin into the e-commerce domain definition."""

    def sync(self, plugin: ProductSourcePlugin, dataset_id: Any, integration_id: Any) -> None:
        """Fetch products via the plugin and upsert each one.

        Products are searched via SQL over their structured attributes, so they are
        not chunked or embedded — only documents go through the vector pipeline.
        """
        for details in plugin.fetch():
            Product.objects.update_or_create(
                dataset_id=dataset_id,
                entry_id=details.entry_id,
                defaults={
                    "integration_id": integration_id,
                    "name": details.name,
                    "slug": details.slug,
                    "sku": details.sku,
                    "description": details.description,
                    "properties": details.properties,
                    "categories": details.categories,
                    "price": details.price,
                },
            )
