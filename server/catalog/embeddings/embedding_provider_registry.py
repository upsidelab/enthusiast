from importlib import import_module

from catalog.embeddings import EmbeddingProvider
from catalog.models import DataSet
from pecl import settings


class EmbeddingProviderRegistry:
    def __init__(self):
        self.providers = settings.CATALOG_EMBEDDING_PROVIDERS

    def provider_for_dataset(self, data_set: DataSet) -> EmbeddingProvider:
        """Retrieves a pre-configured EmbeddingProvider for the specified dataset.
        The method determines the provider class based on the dataset's `embedding_provider` attribute and initializes
        it using the dataset's configured `embedding_model` and `embedding_vector_dimensions`.

        Args:
            data_set (DataSet): The dataset for which the EmbeddingProvider is to be retrieved.
        """
        provider_class_name = self.providers[data_set.embedding_provider]
        module_name, class_name = provider_class_name.rsplit(".", 1)
        module = import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class(data_set.embedding_model, data_set.embedding_vector_dimensions)