from django.db import models
from django.utils import timezone

from catalog.models import DataSet


class AgentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)


class AgentManager(models.Manager):
    def get_queryset(self):
        return AgentQuerySet(self.model, using=self._db).active()


class Agent(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    agent_type = models.CharField(max_length=255, blank=False)
    config = models.JSONField()
    file_upload = models.BooleanField(default=False)

    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="agents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    corrupted = models.BooleanField(default=False)

    objects = AgentManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["dataset", "name"], name="unique_agent_name_per_dataset")]

    def __str__(self):
        return self.name

    def set_deleted_at(self):
        self.deleted_at = timezone.now()
        self.save()
