from django.db import models
from pgvector.django import VectorField

from .document import Document


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
