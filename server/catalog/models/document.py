from django.db import models
from langchain_text_splitters import TokenTextSplitter

from .data_set import DataSet


class Document(models.Model):
    data_set = models.ForeignKey(DataSet, related_name="documents", on_delete=models.PROTECT)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    content = models.TextField()

    class Meta:
        db_table_comment = (
            "List of documents being part of a larger data set. A document may be for instance a blog "
            "post. This is the main entity being analysed by ECL engine when user asks questions "
            "regarding company's offer."
        )
        constraints = [models.UniqueConstraint(fields=["data_set", "url"], name="uq_document")]

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
