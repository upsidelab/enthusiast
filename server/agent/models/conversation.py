from django.contrib.auth import get_user_model
from django.db import models
from enthusiast_common.structures import LLMFile

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
    class FileCategory(models.TextChoices):
        IMAGE = "image", "Image"
        FILE = "file", "File"

    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name="files")
    file = models.FileField(upload_to=conversation_file_path)
    file_category = models.CharField(choices=FileCategory.choices, max_length=32)
    content_type = models.CharField(max_length=255, null=True)
    llm_content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name

    def get_llm_file_object(self):
        return LLMFile(
            id=self.pk,
            content=self.llm_content,
            filename=self.file.name,
            content_type=self.content_type,
            file_category=self.file_category,
        )
