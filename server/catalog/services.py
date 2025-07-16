from typing import Generic, TypeVar

from django.db import models

from agent.registries.embeddings import EmbeddingProviderRegistry
from catalog.models import Document, Product

T = TypeVar("T", bound=models.Model)


class DataSetObjectEmbeddingsGenerator(Generic[T]):
    @staticmethod
    def index_object(obj: T) -> None:
        """Splits the document into chunks and generates embeddings for them using data set's configuration.
        Removes the old chunks and embeddings if present.

        Args:
            obj (Document | Product): The object to (re-)index
        """
        data_set = obj.data_set
        obj.split(data_set.embedding_chunk_size, data_set.embedding_chunk_overlap)
        for chunk in obj.chunks.all():
            embedding_provider_class = EmbeddingProviderRegistry().provider_for_dataset(data_set.id)
            embedding_provider = embedding_provider_class(
                data_set.embedding_model, data_set.embedding_vector_dimensions
            )
            chunk.set_embedding(embedding_provider.generate_embeddings(chunk.content))
            chunk.save()


class ProductEmbeddingGenerator(DataSetObjectEmbeddingsGenerator[Product]):
    pass


class DocumentEmbeddingGenerator(DataSetObjectEmbeddingsGenerator[Document]):
    pass
