from suvereo_common.retrievers import BaseVectorStoreRetriever

from enthusiast_domain.models import DocumentChunk


class DocumentRetriever(BaseVectorStoreRetriever[DocumentChunk]):
    """Retrieves document chunks from the domain definition's DocumentChunk table using vector similarity."""

    chunk_model = DocumentChunk
    dataset_filter = "document__dataset_id"
