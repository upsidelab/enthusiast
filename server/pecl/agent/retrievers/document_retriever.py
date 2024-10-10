from openai import OpenAI
from pgvector.django import CosineDistance

from ecl.models import DocumentEmbedding, Document, DataSet


class DocumentRetriever:
    def __init__(self, data_set: DataSet, model_name: str = "text-embedding-3-large", dimensions: int = 512,
                 max_documents: int = 12):
        self.data_set = data_set
        self.model_name = model_name
        self.dimensions = dimensions
        self.max_documents = max_documents

    def find_documents_matching_query(self, query: str) -> list[Document]:
        embedding_vector = self._create_embedding_for_query(query)
        relevant_documents = self._find_documents_matching_vector(embedding_vector)
        return relevant_documents

    def _create_embedding_for_query(self, query: str) -> list[float]:
        client = OpenAI()
        embeddings = client.embeddings.create(input=query, model=self.model_name, dimensions=self.dimensions)
        return embeddings.data[0].embedding

    def _find_documents_matching_vector(self, embedding_vector: list[float]) -> list[Document]:
        embedding_distance = CosineDistance("embedding", embedding_vector)
        embeddings_by_distance = DocumentEmbedding.objects.annotate(distance=embedding_distance).order_by("distance")
        embeddings_with_documents = embeddings_by_distance.select_related('document').filter(
            document__data_set_id__exact=self.data_set.id)
        limited_embeddings_with_documents = embeddings_with_documents[:self.max_documents]

        return list(map(lambda x: x.document, limited_embeddings_with_documents))
