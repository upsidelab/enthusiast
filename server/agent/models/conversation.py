from django.contrib.auth import get_user_model
from django.db import models

from catalog.models import DataSet


class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=False)
    summary = models.CharField(null=True)
    agent = models.CharField(blank=False, max_length=255, default="Question Answer Agent")

    class Meta:
        db_table_comment = (
            "A conversation is a collection of various messages exchanged during one session. Messages "
            "are mostly questions and answers and have different actors such as end user asking "
            "question and ECL agent answering those questions."
        )
