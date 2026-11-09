from django.db import models
from suvereo_common.indexing import BaseEmbeddingChunk


class DocumentChunk(BaseEmbeddingChunk):
    """A tokenised chunk of a Document's content, with its embedding vector."""

    document = models.ForeignKey(
        "enthusiast_domain.Document",
        on_delete=models.CASCADE,
        related_name="chunks",
    )

