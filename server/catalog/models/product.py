from django.db import models
from langchain_text_splitters import TokenTextSplitter

from .data_set import DataSet


class Product(models.Model):
    data_set = models.ForeignKey(DataSet, on_delete=models.PROTECT, related_name="products")
    entry_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=255, blank=True)
    properties = models.CharField(max_length=65535, blank=True)
    categories = models.CharField(max_length=65535, blank=True)
    price = models.FloatField()

    class Meta:
        db_table_comment = "List of products from a given data set."
        constraints = [models.UniqueConstraint(fields=["data_set", "entry_id"], name="uq_product")]

    def get_content(self):
        return f"{self.name} {self.description}"

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
        chunks = splitter.split_text(self.get_content())

        for chunk in chunks:
            self.chunks.create(product=self, content=chunk)
