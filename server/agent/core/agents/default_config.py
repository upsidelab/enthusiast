from typing import Type

from enthusiast_common.agents import AgentType
from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
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

from agent.core.callbacks import (
    AgentActionWebsocketCallbackHandler,
    ConversationWebSocketCallbackHandler,
    ReactAgentWebsocketCallbackHandler,
)
from agent.core.injector import Injector
from agent.core.registries.embeddings import EmbeddingProviderRegistry
from agent.core.registries.language_models import LanguageModelRegistry
from agent.core.registries.models import BaseDjangoSettingsDBModelRegistry
from agent.core.repositories import (
    DjangoAgentRepository,
    DjangoConversationRepository,
    DjangoDataSetRepository,
    DjangoDocumentChunkRepository,
    DjangoMessageRepository,
    DjangoProductChunkRepository,
    DjangoProductRepository,
    DjangoUserRepository,
)
from agent.core.retrievers import DocumentRetriever, ProductRetriever
from agent.core.retrievers.product_retriever import QUERY_PROMPT_TEMPLATE


class DefaultAgentConfig(BaseModel):
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[Injector]
    registry: RegistryConfig
    llm: LLMConfig
    agent_callback_handler: AgentCallbackHandlerConfig | None = None


def get_default_config(type: AgentType) -> DefaultAgentConfig:
    llm_callback_handler_class = (
        ReactAgentWebsocketCallbackHandler if type == AgentType.RE_ACT else ConversationWebSocketCallbackHandler
    )
    agent_callback_handler_config = (
        AgentCallbackHandlerConfig(handler_class=AgentActionWebsocketCallbackHandler)
        if type == AgentType.RE_ACT
        else None
    )
    return DefaultAgentConfig(
        repositories=RepositoriesConfig(
            user=DjangoUserRepository,
            data_set=DjangoDataSetRepository,
            conversation=DjangoConversationRepository,
            message=DjangoMessageRepository,
            product=DjangoProductRepository,
            document_chunk=DjangoDocumentChunkRepository,
            product_chunk=DjangoProductChunkRepository,
            agent=DjangoAgentRepository,
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
                CallbackHandlerConfig(handler_class=llm_callback_handler_class),
            ],
        ),
        agent_callback_handler=agent_callback_handler_config,
    )


def merge_config(
    partial: AgentConfigWithDefaults,
) -> AgentConfig:
    merged: dict[str, object] = {}
    defaults = get_default_config(type=partial.agent_class.AGENT_TYPE)
    for name in AgentConfig.model_fields:
        value = getattr(partial, name, None)

        if value is not None:
            merged[name] = value
        else:
            merged[name] = getattr(defaults, name, None)

    return AgentConfig(**merged)
