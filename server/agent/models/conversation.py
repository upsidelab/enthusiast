from django.contrib.auth import get_user_model
from django.db import models

from agent.models.agent import Agent
from catalog.models import DataSet


def conversation_file_path(instance, filename):
    return f"conversations/{instance.conversation.id}/{filename}"


class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=False)
    summary = models.CharField(null=True)
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, null=False)

    class Meta:
        db_table_comment = (
            "A conversation is a collection of various messages exchanged during one session. Messages "
            "are mostly questions and answers and have different actors such as end user asking "
            "question and ECL agent answering those questions."
        )


class ConversationFile(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name="files")
    file = models.FileField(upload_to=conversation_file_path)
    content_type = models.CharField(max_length=255, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name
