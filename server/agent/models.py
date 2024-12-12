from django.contrib.auth import get_user_model
from django.db import models
from pgvector.django import VectorField

from agent.core import Agent
from catalog.models import DataSet

from langchain_core.messages import AIMessage, HumanMessage


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
        for message in self.message.all().order_by('id'):
            if message.role == 'user':
                history.append(HumanMessage(content=message.text or ""))
            elif message.role == 'agent':
                history.append(AIMessage(content=message.text or ""))
            else:
                raise Exception(f"Unregistered role: '{message.role}'. Unable to retrieve conversation history.")
        return history


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="message", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=15)
    text = models.TextField()
    # Feedback regarding a message (for instance: feedback regarding answer provided by agent).
    rating = models.IntegerField(null=True)  # Category (range bad->good represented as number).
    feedback = models.TextField(null=True)  # Free text to provide information regarding answer's accuracy.


    class Meta:
        db_table_comment = ("A message sent during a conversation. Role describes category of a message, it may be "
                            "a question asked by a user, agent's answer, or system message.")


class Question(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="question", on_delete=models.PROTECT)
    asked_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    question_embedding = VectorField(null=True)
    prompt_message = models.TextField(null=True)
    answer = models.TextField(null=True)
    answer_embedding = VectorField(null=True)
    # User's feedback regarding answer provided by agent.
    answer_rating = models.IntegerField(null=True)  # Category (range bad->good represented as number).
    answer_feedback = models.TextField(null=True)  # Free text to provide information regarding answer's accuracy.

    class Meta:
        db_table_comment = "A question is a collection of two messages: question itself followed by a system's answer."

    def get_answer(self):
        """Formulate an answer to a given question and store the decision-making process.

        Engine calculates embedding for a question and using similarity search collects documents that may contain
        relevant content.
        """
        agent = Agent(data_set=self.conversation.data_set,
                      messages=self.conversation.get_messages())
        response = agent.process_user_request(self.question)

        self.answer = response["output"]

