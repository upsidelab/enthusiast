from django.db import models

from catalog.models import DataSet


class AgentConfiguration(models.Model):
    name = models.CharField(max_length=255, unique=True)

    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    config = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
