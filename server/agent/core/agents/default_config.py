from typing import Type

from enthusiast_common.config import (
    AgentConfig,
    AgentConfigWithDefaults,
    EmbeddingsRegistryConfig,
    LLMRegistryConfig,
    ModelsRegistryConfig,
    RegistryConfig,
    RepositoriesConfig,
    RetrieverConfig,
    RetrieversConfig,
)
from pydantic import BaseModel

from agent.injector import Injector
from agent.registries.embeddings import EmbeddingProviderRegistry
from agent.registries.language_models import LanguageModelRegistry
from agent.registries.models import BaseDjangoSettingsDBModelRegistry
from agent.repositories import (
    DjangoConversationRepository,
    DjangoDataSetRepository,
    DjangoDocumentChunkRepository,
    DjangoMessageRepository,
    DjangoProductChunkRepository,
    DjangoProductRepository,
    DjangoUserRepository,
)
from agent.retrievers import DocumentRetriever, ProductRetriever
from agent.retrievers.product_retriever import QUERY_PROMPT_TEMPLATE


class DefaultAgentConfig(BaseModel):
    repositories: RepositoriesConfig = RepositoriesConfig(
        user=DjangoUserRepository,
        data_set=DjangoDataSetRepository,
        conversation=DjangoConversationRepository,
        message=DjangoMessageRepository,
        product=DjangoProductRepository,
        document_chunk=DjangoDocumentChunkRepository,
        product_chunk=DjangoProductChunkRepository,
    )
    retrievers: RetrieversConfig = RetrieversConfig(
        document=RetrieverConfig(retriever_class=DocumentRetriever),
        product=RetrieverConfig(
            retriever_class=ProductRetriever,
            extra_kwargs={
                "prompt_template": QUERY_PROMPT_TEMPLATE,
                "max_sample_products": 12,
                "number_of_products": 12,
            },
        ),
    )
    injector: Type[Injector] = Injector
    registry: RegistryConfig = RegistryConfig(
        llm=LLMRegistryConfig(registry_class=LanguageModelRegistry),
        embeddings=EmbeddingsRegistryConfig(registry_class=EmbeddingProviderRegistry),
        model=ModelsRegistryConfig(registry_class=BaseDjangoSettingsDBModelRegistry),
    )


def merge_config(
    partial: AgentConfigWithDefaults,
    defaults: type[DefaultAgentConfig] = DefaultAgentConfig,
) -> AgentConfig:
    default_values = defaults()
    merged: dict[str, object] = {}

    for name in AgentConfig.model_fields:
        value = getattr(partial, name, None)

        if value is not None:
            merged[name] = value
        else:
            merged[name] = getattr(default_values, name, None)

    return AgentConfig(**merged)
