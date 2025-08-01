from typing import Type

from enthusiast_common.config import (
    AgentConfig,
    AgentConfigWithDefaults,
    CallbackHandlerConfig,
    EmbeddingsRegistryConfig,
    LLMConfig,
    LLMRegistryConfig,
    ModelsRegistryConfig,
    RegistryConfig,
    RepositoriesConfig,
    RetrieverConfig,
    RetrieversConfig,
)
from pydantic import BaseModel

from agent.core.callbacks import ConversationWebSocketCallbackHandler
from agent.core.injector import Injector
from agent.core.repositories import (
    DjangoConversationRepository,
    DjangoDataSetRepository,
    DjangoDocumentChunkRepository,
    DjangoMessageRepository,
    DjangoProductChunkRepository,
    DjangoProductRepository,
    DjangoUserRepository,
)
from agent.registries.embeddings import EmbeddingProviderRegistry
from agent.registries.language_models import LanguageModelRegistry
from agent.registries.models import BaseDjangoSettingsDBModelRegistry
from agent.retrievers import DocumentRetriever, ProductRetriever
from agent.retrievers.product_retriever import QUERY_PROMPT_TEMPLATE


class DefaultAgentConfig(BaseModel):
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[Injector]
    registry: RegistryConfig
    llm: LLMConfig


def get_default_config(conversation_id: int, streaming: bool) -> DefaultAgentConfig:
    return DefaultAgentConfig(
        repositories=RepositoriesConfig(
            user=DjangoUserRepository,
            data_set=DjangoDataSetRepository,
            conversation=DjangoConversationRepository,
            message=DjangoMessageRepository,
            product=DjangoProductRepository,
            document_chunk=DjangoDocumentChunkRepository,
            product_chunk=DjangoProductChunkRepository,
        ),
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(
                retriever_class=ProductRetriever,
                extra_kwargs={
                    "prompt_template": QUERY_PROMPT_TEMPLATE,
                    "max_sample_products": 12,
                    "number_of_products": 12,
                },
            ),
        ),
        injector=Injector,
        registry=RegistryConfig(
            llm=LLMRegistryConfig(registry_class=LanguageModelRegistry),
            embeddings=EmbeddingsRegistryConfig(registry_class=EmbeddingProviderRegistry),
            model=ModelsRegistryConfig(registry_class=BaseDjangoSettingsDBModelRegistry),
        ),
        llm=LLMConfig(
            callbacks=[
                CallbackHandlerConfig(
                    handler_class=ConversationWebSocketCallbackHandler, args={"conversation_id": conversation_id}
                ),
            ],
            streaming=streaming,
        ),
    )


def merge_config(
    partial: AgentConfigWithDefaults,
    conversation_id: int,
    streaming: bool,
) -> AgentConfig:
    merged: dict[str, object] = {}
    defaults = get_default_config(conversation_id=conversation_id, streaming=streaming)
    for name in AgentConfig.model_fields:
        value = getattr(partial, name, None)

        if value is not None:
            merged[name] = value
        else:
            merged[name] = getattr(defaults, name, None)

    return AgentConfig(**merged)
