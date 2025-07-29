from django.db import models

from catalog.models import DataSet


class Agent(models.Model):
    name = models.CharField(max_length=255, unique=True)
    agent_type = models.CharField(max_length=255, blank=False)
    config = models.JSONField()

    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="agents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["dataset", "name"], name="unique_agent_name_per_dataset")]

    def __str__(self):
        return self.name
