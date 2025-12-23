from django.db import models

from .data_set import DataSet


class ProductSource(models.Model):
    plugin_name = models.CharField()
    data_set = models.ForeignKey(DataSet, related_name="product_sources", on_delete=models.PROTECT)
    config = models.JSONField(default=dict, null=True)
    corrupted = models.BooleanField(default=False)
