from django.db import models
from suvereo_common.entities import DomainEntity, EntityField


class Product(DomainEntity, models.Model):
    """A product synced from an external source, searched via SQL over its attributes."""

    dataset = models.ForeignKey("catalog.DataSet", on_delete=models.CASCADE, related_name="products")
    integration = models.ForeignKey(
        "catalog.Integration", on_delete=models.CASCADE, related_name="products", null=True, blank=True
    )
    entry_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255, blank=True)
    properties = models.CharField(max_length=65535, blank=True)
    categories = models.CharField(max_length=65535, blank=True)
    price = models.FloatField()

    class Meta:
        db_table_comment = "List of products from a given data set."
        constraints = [models.UniqueConstraint(fields=["dataset", "entry_id"], name="uq_ecommerce_product")]

    class EntityMeta:
        slug = "products"
        label = "Products"
        list_fields = [
            EntityField("name"),
            EntityField("sku"),
            EntityField("price"),
        ]

    def __str__(self):
        return self.name
