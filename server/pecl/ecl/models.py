from django.db import models
from openai import OpenAI
from pgvector.django import CosineDistance, VectorField


class EmbeddingModel(models.Model):
    """ECL Config - list of models to be used."""
    code = models.CharField(max_length=5, default="UNSET")
    name = models.CharField(max_length=30)


class EmbeddingDimension(models.Model):
    """ECL Config - list of LLM vector lengths to be used for embeddings."""
    dimension = models.IntegerField()


class DataSet(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30)

    def reload_all_embeddings(self):
        """Reloads embeddings for all models and dimensions registered in ECL config.

        Note: this will recalculate only those combinations which are currently defined in ECL config.
        If there are other combinations already stored, those will not be changed. This may happen when
        embeddings for model ALFA and dimensions 216 were calculated before, while now ECL config is set to
        calculate embeddings with model BETA and dimensions set to 1536.
        """
        embedding_models = EmbeddingModel.objects.all()
        embedding_dimensions = EmbeddingDimension.objects.all()

        for m in embedding_models:
            for d in embedding_dimensions:
                self.set_content_embeddings(m, d.dimension)


    def set_content_embeddings(self, model, dimensions):
        """Sets embeddings with a given model and dimension for all the content of the company.

         Embeddings are sourced from OpenAI, args define how we generate embeddings. We would like to
         be able to generate embeddings multiple times for different models and dimensions combinations.

         One content (such as a blog post) may have multiple embeddings calculated. Thanks to this approach
         we are able to precalculate different vectors and flexibly switch between those on admin panel level.

         Args:
             model: EmbeddingModel, ID of an OpenAI model used to generate embeddings.
             dimensions: Integer, length of an embedding vector.
         """
        cnt = 0
        for document in self.document.all():
            cnt += 1
            document.set_embedding(model, dimensions)


class Document(models.Model):
    data_set = models.ForeignKey("DataSet", related_name="document", on_delete=models.SET_NULL, null=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    def set_embedding(self, model, dimensions):
        """Sets embeddings with a given model and dimension for this content.

         For more info please refer to docs on a Company level (parent of this entity).

         Args:
             model: Integer, ID of an OpenAI model used to generate embeddings.
             dimensions: Integer, length of an embedding model.
         """
        # Obtain a new embedding vector for this content.
        client = OpenAI()
        try:
            openai_embedding = client.embeddings.create(model=model.name,
                                                        dimensions=dimensions,
                                                        input=self.content)
            embedding_vector = openai_embedding.data[0].embedding

            # Upsert a new embedding. TODO: prettify upsert method (remove for).
            cnt = 0
            for emb in self.embedding.all().filter(dimensions=dimensions):
                emb.set_embedding(model=model, dimensions=dimensions, embedding_vector=embedding_vector)
                cnt += 1

            if cnt == 0:
                new_emb = DocumentEmbedding(document=self,
                                            model=model,
                                            dimensions=dimensions,
                                            embedding=embedding_vector
                                            )
                new_emb.save()


        except Exception as error:
            pass  #TODO: add error handling (planned along with logging module)


class DocumentEmbedding(models.Model):
    document = models.ForeignKey("Document", related_name="embedding", on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey("EmbeddingModel", on_delete=models.SET_NULL, null=True)
    dimensions = models.IntegerField()
    embedding = VectorField()

    def set_embedding(self, model, dimensions, embedding_vector):
        """Sets embedding vector for given model and dimensions.

        For more info regarding embedding calculation please refer to docs on a Company level.

        Args:
            model: Integer, ID of an OpenAI model used to generate embeddings.
            dimensions: Integer, length of an embedding model.
            embedding_vector: VectorField, LLM vector with a given dimension.
        """
        self.model = model
        self.dimensions = dimensions
        self.embedding = embedding_vector


class Product(models.Model):
    company_code = models.ForeignKey("DataSet", on_delete=models.SET_NULL, null=True)
    entry_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255)
    properties = models.CharField(max_length=65535)
    categories = models.CharField(max_length=65535)
    price = models.FloatField()


class Conversation(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(EmbeddingModel, related_name="conversation", on_delete=models.SET_NULL, null=True)
    dimensions = models.IntegerField(null=True)
    user_name = models.CharField(max_length=50, default="user")  # Who asks questions.
    system_name = models.CharField(max_length=50, default="system")  # Who answers.

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
    conversation = models.ForeignKey(Conversation, related_name="question", on_delete=models.SET_NULL, null=True)
    asked_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    question_embedding = VectorField(null=True)
    answer = models.TextField(null=True)
    answer_embedding = VectorField(null=True)

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
        client = OpenAI()

        # Calculate embedding for a question.
        openai_embedding = client.embeddings.create(model=self.conversation.model.name,
                                                    dimensions=self.conversation.dimensions,
                                                    input=self.question)
        self.question_embedding = openai_embedding.data[0].embedding

        # Aggregate distance for Documents.
        embedding_with_distance = DocumentEmbedding.objects.filter(dimensions=self.conversation.dimensions).annotate(
            distance=CosineDistance("embedding", self.question_embedding)
        ).order_by("distance")[:12]

        # Persist an answer details.
        for doc in embedding_with_distance:
            ad = AnswerDocument()
            ad.conversation = self.conversation
            ad.question = self
            ad.document = doc.document
            ad.document_embedding = doc
            ad.document_title = doc.document.title
            ad.cosine_distance = doc.distance
            ad.save()

        # Get the document content aware answer for a user's question.
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user",
                       "content": f"Based on the following content delimited by three backticks ```{embedding_with_distance[0].document.content}``` write an answer to the following request ${self.question}"}
        ])

        self.answer = completion.choices[0].message.content


class AnswerDocument(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="answer_document", on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Question, related_name="answer_document", on_delete=models.SET_NULL, null=True)
    document = models.ForeignKey(Document, related_name="answer_document", on_delete=models.SET_NULL, null=True)
    document_embedding = models.ForeignKey(DocumentEmbedding, related_name="answer_document", on_delete=models.SET_NULL, null=True)
    document_title = models.CharField(max_length=1024)
    cosine_distance = models.FloatField(null=True)

    class Meta:
        db_table_comment = "Document considered by our similarity search engine as similar to the question. Documents from this table were used to formulate the answer"
        db_table = "ecl_answer_document"
