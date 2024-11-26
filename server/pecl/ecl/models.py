import logging

from langchain.text_splitter import TokenTextSplitter

from django.db import models
from openai import OpenAI
from pgvector.django import VectorField
from django.conf import settings


logger = logging.getLogger(__name__)


class EmbeddingModel(models.Model):
    """ECL Config - list of models to be used."""
    code = models.CharField(max_length=5, null=True)  # Short name - to be displayed on UI
    name = models.CharField(max_length=30, unique=True)  # Full name of a model

    class Meta:
        db_table_comment = ("Models used to create embedding vectors. Note: all models from this table will be used "
                            "when action 'reload all embeddings' is performed by admin.")
        db_table = "ecl_embedding_model"


class EmbeddingDimension(models.Model):
    """ECL Config - list of LLM vector lengths to be used for embeddings."""
    dimension = models.IntegerField(unique=True)

    class Meta:
        db_table_comment = ("Lengths of embedding vector that are collected from OpenAI for documents or products. For "
                            "one item we may collect multiple embedding vectors of different lengths. Note: vectors "
                            "for all dimensions from this table will be collected when action 'reload all embeddings' "
                            "is performed by admin.")
        db_table = "ecl_embedding_dimension"

class DataSet(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="data_sets")

    class Meta:
        db_table_comment = ("List of various data sets. One data set may be the whole company's content such as blog "
                            "posts, or some part of it: a data set may be represent a brand or department.")
        db_table = "ecl_data_set"

    def async_reload_all_embeddings(self):
        from .tasks import reload_all_embeddings_task

        logging.info("Models/Start async reload all embeddings task")
        reload_all_embeddings_task.apply_async(args=[self.id])
        logging.info("Models/Stop async reload all embeddings task")

    def reindex_documents(self, **kwargs):
        """Recreate the whole structure used by ECL to process user's question.

        This method does not change data sets. It recreates internal layer that is calculated after the raw data set is
        imported. Data set consists of different objects such as products and documents. To be able to process user's
        questions we have to split larger documents into chunks and collect embeddings for them.

        **kwargs:
            chunk_size (int, optional): maximum number tokens per one chunk.
            chunk_overlap (int, optional): an overlap between neighbouring chunks.
        """
        self.split_documents(**kwargs)
        self.reload_all_embeddings()

    def reload_all_embeddings(self):
        """Reloads embeddings for all models and dimensions registered in ECL config.

        Note: this will recalculate only those combinations which are currently defined in ECL config.
        If there are other combinations already stored, those will not be changed. This may happen when
        embeddings for model ALFA and dimensions 216 were calculated before, while now ECL config is set to
        calculate embeddings with model BETA and dimensions set to 1536.
        """
        logging.info("Start reload all embeddings method")
        embedding_models = EmbeddingModel.objects.all()
        embedding_dimensions = EmbeddingDimension.objects.all()

        for model in embedding_models:
            logging.info(f"- reload embeddings for model: {model.name}")
            for dimension in embedding_dimensions:
                logging.info(f"- reload embeddings for dimension: {dimension.dimension}")
                self.set_embeddings(model, dimension)
        logging.info("Stop reload all embeddings method")


    def set_embeddings(self, model, dimensions):
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
            document.set_embeddings(model, dimensions)

    def split_documents(self, **kwargs):
        """Split documents into chunks with a defined overlap.

        **kwargs:
            chunk_size (int, optional): maximum number tokens per one chunk.
            chunk_overlap (int, optional): an overlap between neighbouring chunks.
        """
        logging.info("Start recreating document chunks")
        for document in self.document.all():
            document.split(**kwargs)
        logging.info("Stop recreating document chunks")

class Document(models.Model):
    data_set = models.ForeignKey(DataSet, related_name="document", on_delete=models.PROTECT, null=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    class Meta:
        db_table_comment = ("List of documents being part of a larger data set. A document may be for instance a blog "
                            "post. This is the main entity being analysed by ECL engine when user asks questions "
                            "regarding company's offer.")

    def split(self, **kwargs):
        """Split document into chunks that fit embedding model limits.

        A document is split into one or more chunks that overlap each other. Chunks are used to provide context
        for user's questions. Golden rule: a chunk must fit within embedding model token limit: long documents that
        exceed this limit are divided into several smaller chunks, shorter documents consist of one chunk.

        **kwargs:
            chunk_size (int, optional): maximum number tokens per one chunk.
            chunk_overlap (int, optional): an overlap between neighbouring chunks.
        """
        # Configure splitter.
        chunk_size = kwargs.get("chunk_size", 3000)
        chunk_overlap = kwargs.get("chunk_overlap", 150)
        # Delete old chunks.
        self.chunk.all().delete()
        # Create new chunks.
        splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        chunks = splitter.split_text(self.content)

        for chunk in chunks:
            DocumentChunk.objects.create(document=self, content=chunk)

    def set_embeddings(self, model, dimensions):
        for chunk in self.chunk.all():
            chunk.set_embedding(model, dimensions)


class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, related_name="chunk", on_delete=models.CASCADE, null=False)
    content = models.TextField()

    def set_embedding(self, model, dimensions):
        """Sets embeddings with a given model and dimension for this content.

         For more info please refer to docs on a Company level (parent of this entity).

         Args:
             model: EmbeddingModel, represents an OpenAI model used to generate embeddings.
             dimensions: EmbeddingDimension, represents length of an embedding vector.
         """
        # Delete old embeddings.
        self.embedding.filter(model=model, dimensions=dimensions).delete()
        # Obtain a new embedding vector for this content.
        client = OpenAI()

        openai_embedding = client.embeddings.create(model=model.name,
                                                    dimensions=dimensions.dimension,
                                                    input=self.content)
        embedding_vector = openai_embedding.data[0].embedding

        # Create a new embedding.
        DocumentChunkEmbedding.objects.create(chunk=self,
                                              model=model,
                                              dimensions=dimensions,
                                              embedding=embedding_vector)


class DocumentChunkEmbedding(models.Model):
    chunk = models.ForeignKey(DocumentChunk, related_name="embedding", on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(EmbeddingModel, on_delete=models.PROTECT, null=True)
    dimensions = models.ForeignKey(EmbeddingDimension, on_delete=models.PROTECT, null=True)
    embedding = VectorField()

    class Meta:
        db_table_comment = ("Embedding vectors collected for one chunk. One chunk may have several different "
                            "embedding vectors which have different dimensions. Agent processing user's questions "
                            "chooses the best vector for the purpose.")
        constraints = [
            models.UniqueConstraint(fields=['chunk', 'model', 'dimensions'], name="document_chunk_embedding_uk")
        ]


class Product(models.Model):
    company_code = models.ForeignKey(DataSet, on_delete=models.PROTECT, null=True)
    entry_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255)
    properties = models.CharField(max_length=65535)
    categories = models.CharField(max_length=65535)
    price = models.FloatField()

    class Meta:
        db_table_comment = "List of a company's products."

