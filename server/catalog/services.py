from catalog.embeddings import EmbeddingProviderRegistry
from catalog.models import Document


def index_document(document: Document):
    """Splits the document into chunks and generates embeddings for them using data set's configuration.
    Removes the old chunks and embeddings if present.

    Args:
        document (Document): The document to (re-)index
    """
    data_set = document.data_set
    document.split(data_set.embedding_chunk_size, data_set.embedding_chunk_overlap)
    for chunk in document.chunks.all():
        embedding_provider = EmbeddingProviderRegistry().provider_for_dataset(data_set)
        chunk.set_embedding(embedding_provider.generate_embeddings(chunk.content))
