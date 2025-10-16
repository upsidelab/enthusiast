from django.db import models

from .conversation import Conversation


class Message(models.Model):
    class MessageType(models.TextChoices):
        FUNCTION = "function"
        HUMAN = "human"
        AI = "ai"
        SYSTEM = "system"
        INTERMEDIATE_STEP = "intermediate_step"
        FILE = "file"

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    type = models.CharField(max_length=50, choices=MessageType.choices)

    rating = models.IntegerField(null=True)
    feedback = models.TextField(null=True)

    answer_failed = models.BooleanField(default=False)
    function_name = models.CharField(max_length=50, blank=True, null=True)

    @classmethod
    def internal_message_types(cls):
        return [cls.MessageType.FUNCTION, cls.MessageType.FILE, cls.MessageType.INTERMEDIATE_STEP]

    @property
    def langchain_type(self):
        langchain_type_mapping = {
            self.MessageType.FUNCTION: "ai",
            self.MessageType.FILE: "human",
            self.MessageType.INTERMEDIATE_STEP: "ai",
            self.MessageType.HUMAN: "human",
            self.MessageType.AI: "ai",
            self.MessageType.SYSTEM: "system",
        }
        return langchain_type_mapping[self.type]

    class Meta:
        db_table_comment = (
            "A message sent during a conversation. Role describes category of a message, it may be "
            "a question asked by a user, agent's answer, or system message."
        )
