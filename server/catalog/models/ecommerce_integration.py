from django.db import models

from .data_set import DataSet


class ECommerceIntegration(models.Model):
    plugin_name = models.CharField()
    data_set = models.OneToOneField(DataSet, related_name="ecommerce_integration", on_delete=models.PROTECT)
    config = models.JSONField(default=dict)
