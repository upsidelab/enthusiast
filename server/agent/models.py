from django.contrib.auth import get_user_model
from django.db import models
from langchain_core.messages import AIMessage, HumanMessage

from catalog.models import DataSet


class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    system_name = models.CharField(max_length=50, default="system", null=True)  # Who answers.
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=False)

    class Meta:
        db_table_comment = ("A conversation is a collection of various messages exchanged during one session. Messages "
                            "are mostly questions and answers and have different actors such as end user asking "
                            "question and ECL agent answering those questions.")

    def get_messages(self):
        """Return list of messages exchanged during a conversation.
        """
        history = []
        for message in self.messages.all().order_by('id'):
            if message.role == 'user':
                history.append(HumanMessage(content=message.text or ""))
            elif message.role == 'agent':
                history.append(AIMessage(content=message.text or ""))

        return history


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=15)
    text = models.TextField()
    # Feedback regarding a message (for instance: feedback regarding answer provided by agent).
    rating = models.IntegerField(null=True)  # Category (range bad->good represented as number).
    feedback = models.TextField(null=True)  # Free text to provide information regarding answer's accuracy.

    class Meta:
        db_table_comment = ("A message sent during a conversation. Role describes category of a message, it may be "
                            "a question asked by a user, agent's answer, or system message.")
