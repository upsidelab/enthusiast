from django.contrib.auth import get_user_model
from django.db import models
from langchain_core.messages import HumanMessage, AIMessage

from catalog.models import DataSet


class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=False)
    summary = models.CharField(null=True)

    class Meta:
        db_table_comment = (
            "A conversation is a collection of various messages exchanged during one session. Messages "
            "are mostly questions and answers and have different actors such as end user asking "
            "question and ECL agent answering those questions."
        )

    def get_messages(self):
        """Return list of messages exchanged during a conversation."""
        history = []
        for message in self.messages.all().order_by("id"):
            if message.role == "user":
                history.append(HumanMessage(content=message.text or ""))
            elif message.role == "agent":
                history.append(AIMessage(content=message.text or ""))

        return history
