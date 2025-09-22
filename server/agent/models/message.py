from django.db import models
from enthusiast_common.registry import LanguageModelProvider

from .conversation import Conversation


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=15)
    text = models.TextField()

    rating = models.IntegerField(null=True)
    feedback = models.TextField(null=True)

    answer_failed = models.BooleanField(default=False)
    is_file = models.BooleanField(default=False)

    def parse_file_id(self) -> int | None:
        if not self.is_file:
            return None
        return int(self.text.removeprefix(LanguageModelProvider.FILE_KEY_PREFIX))

    class Meta:
        db_table_comment = (
            "A message sent during a conversation. Role describes category of a message, it may be "
            "a question asked by a user, agent's answer, or system message."
        )
