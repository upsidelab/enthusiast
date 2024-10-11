from django.db import models
from pgvector.django import VectorField

from agent.core import Agent
from ecl.models import EmbeddingModel, DocumentEmbedding, Document, DataSet, EmbeddingDimension


class Conversation(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(EmbeddingModel, related_name="conversation", on_delete=models.PROTECT, null=True)
    dimensions = models.ForeignKey(EmbeddingDimension, on_delete=models.PROTECT, null=True)
    user_name = models.CharField(max_length=50, default="user", null=True)  # Who asks questions.
    system_name = models.CharField(max_length=50, default="system", null=True)  # Who answers.
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=False)

    class Meta:
        db_table_comment = "A conversation is a collection of various messages exchanged during one session. Messages are mostly questions and answers and have different actors such as end user asking question and ECL agent answering those questions."

    def get_history(self):
        """Return list of messages exchanged during a conversation.

        Messages are stored as an object and may be used by various clients such as html template
        to display history of a conversation on the conversation page.
        """
        history = []
        for question in self.question.all():
            history += question.get_qa_str()
        return history


class Question(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="question", on_delete=models.PROTECT)
    asked_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    question_embedding = VectorField(null=True)
    prompt_message = models.TextField(null=True, default=None)
    answer = models.TextField(null=True)
    answer_embedding = VectorField(null=True)

    class Meta:
        db_table_comment = "A question is a collection of two messages: question itself followed by a system's answer."

    def get_qa_str(self):
        """Return two messages: question and answer.

        A question in our model question entity consists of two actions: a question asked is followed by an answer.
        Hence, for one question there are two messages in a conversation.
        """
        return [{"sender": "user", "name": self.conversation.user_name, "text": self.question},
                {"sender": "system", "name": self.conversation.system_name, "text": self.answer}]

    def get_answer(self):
        """Formulate an answer to a given question and store the decision-making process.

        Engine calculates embedding for a question and using similarity search collects documents that may contain
        relevant content.
        """
        agent = Agent(data_set=self.conversation.data_set,
                      embedding_model=self.conversation.model,
                      embedding_dimensions=self.conversation.dimensions)
        response = agent.process_user_request(self.question)

        self.answer = response["output"]


class AnswerDocument(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="answer_document", on_delete=models.PROTECT)
    question = models.ForeignKey(Question, related_name="answer_document", on_delete=models.PROTECT)
    document = models.ForeignKey(Document, related_name="answer_document", on_delete=models.PROTECT)
    document_embedding = models.ForeignKey(DocumentEmbedding, related_name="answer_document", on_delete=models.PROTECT,
                                           null=True)
    document_title = models.CharField(max_length=1024)
    cosine_distance = models.FloatField(null=True)

    class Meta:
        db_table_comment = "Document considered by our similarity search engine as relevant to the question. Documents from this table are used to formulate the answer."
        db_table = "agent_answer_document"
