from django.db import models

from .conversation import Conversation


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=15)
    text = models.TextField()

    rating = models.IntegerField(null=True)
    feedback = models.TextField(null=True)

    class Meta:
        db_table_comment = (
            "A message sent during a conversation. Role describes category of a message, it may be "
            "a question asked by a user, agent's answer, or system message."
        )
