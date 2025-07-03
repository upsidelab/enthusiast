from abc import ABC, abstractmethod
from typing import Any, Self


class BaseRetriever(ABC):
    @classmethod
    @abstractmethod
    def create(
        cls,
        config: "AgentConfig",  # noqa: F821
        data_set_id: Any,
        repositories: "RepositoriesInstances",  # noqa: F821
        embeddings_registry: "BaseEmbeddingProviderRegistry",  # noqa: F821
        llm: "BaseLLM",  # noqa: F821
    ) -> Self:
        pass
