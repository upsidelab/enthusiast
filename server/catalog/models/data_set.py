from django.conf import settings
from django.db import models


class DataSet(models.Model):
    name = models.CharField(max_length=30)
    language_model_provider = models.CharField(default="OpenAI")
    language_model = models.CharField(default="gpt-4o")
    embedding_provider = models.CharField(max_length=255, default="OpenAI")
    embedding_model = models.CharField(max_length=255, default="text-embedding-3-large")
    embedding_vector_dimensions = models.IntegerField(default=512)
    embedding_chunk_size = models.IntegerField(default=3000)
    embedding_chunk_overlap = models.IntegerField(default=150)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="data_sets")

    class Meta:
        db_table_comment = (
            "List of various data sets. One data set may be the whole company's content such as blog "
            "posts, or some part of it: a data set may be represent a brand or department."
        )
        permissions = [
            ("manage_dataset_users", "Can manage users of a dataset"),
        ]
