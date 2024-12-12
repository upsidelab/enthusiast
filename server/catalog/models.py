import logging

from django.conf import settings
from django.db import models
from langchain.text_splitter import TokenTextSplitter
from pgvector.django import VectorField

logger = logging.getLogger(__name__)


class DataSet(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=30)
    embedding_provider = models.CharField(max_length=255, default="OpenAI")
    embedding_model = models.CharField(max_length=255, default="text-embedding-3-large")
    embedding_vector_dimensions = models.IntegerField(default=512)
    embedding_chunk_size = models.IntegerField(default=3000)
    embedding_chunk_overlap = models.IntegerField(default=150)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="data_sets")

    class Meta:
        db_table_comment = ("List of various data sets. One data set may be the whole company's content such as blog "
                            "posts, or some part of it: a data set may be represent a brand or department.")



class ProductSource(models.Model):
    plugin_name = models.CharField()
    data_set = models.ForeignKey(DataSet, related_name="product_sources", on_delete=models.PROTECT)
    config = models.JSONField(default=dict, null=True)


class DocumentSource(models.Model):
    plugin_name = models.CharField()
    data_set = models.ForeignKey(DataSet, related_name="document_sources", on_delete=models.PROTECT)
    config = models.JSONField(default=dict, null=True)


class Document(models.Model):
    data_set = models.ForeignKey(DataSet, related_name="documents", on_delete=models.PROTECT)
    url = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    class Meta:
        db_table_comment = ("List of documents being part of a larger data set. A document may be for instance a blog "
                            "post. This is the main entity being analysed by ECL engine when user asks questions "
                            "regarding company's offer.")

    def split(self, chunk_size, chunk_overlap):
        """
        Split a document into chunks that comply with the embedding model's token limits, removing old chunks if present.

        This function splits a document into one or more overlapping chunks to provide context for user queries.
        The main rule is that each chunk must stay within the token limit of the embedding model.
        For long documents that exceed this limit, the document is divided into multiple smaller chunks,
        while shorter documents are represented as a single chunk.
        If old chunks are present, they are removed before creating new ones.

        Args:
            chunk_size (int): The maximum number of tokens allowed in a single chunk.
            chunk_overlap (int): The number of overlapping tokens between adjacent chunks.
        """
        self.chunks.all().delete()

        splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(self.content)

        for chunk in chunks:
            self.chunks.create(document=self, content=chunk)


class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, related_name="chunks", on_delete=models.CASCADE)
    content = models.TextField()
    embedding = VectorField(null=True)

    def set_embedding(self, embedding_vector: list[float]):
        """Sets the embedding vector for this document chunk.

        Args:
            embedding_vector (list[float]): The embedding vector to associate with the document chunk.
        """
        self.embedding = embedding_vector


class Product(models.Model):
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, related_name="products")
    entry_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255)
    properties = models.CharField(max_length=65535)
    categories = models.CharField(max_length=65535)
    price = models.FloatField()

    class Meta:
        db_table_comment = "List of products from a given data set."

