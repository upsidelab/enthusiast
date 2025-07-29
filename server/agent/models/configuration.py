from django.db import models

from catalog.models import DataSet


class AgentConfiguration(models.Model):
    name = models.CharField(max_length=255, unique=True)
    agent_key = models.CharField(max_length=255, blank=False)
    config = models.JSONField()

    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
