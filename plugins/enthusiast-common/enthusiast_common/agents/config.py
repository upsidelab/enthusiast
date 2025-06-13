from typing import Type, Optional, Sequence

from django.db import models
from langchain.agents import AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass, field

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.chat import MessageLikeRepresentation

from .base import BaseAgent
from ..services.conversation import ConversationService
from ..tools import BaseAgentTool, BaseLLMTool, BaseFunctionTool
from ..llm import BaseLLM
from ..registry import (
    BaseDjangoSettingsModelRegistry,
    BaseLanguageModelRegistry,
    BaseEmbeddingProviderRegistry,
    BaseDjangoSettingsEmbeddingRegistry,
)
from ..repositories.base import (
    BaseUserRepository,
    BaseMessageRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseProductRepository,
    BaseRepository,
    BaseDocumentChunkRepository,
)
from ..repositories.django import (
    DjangoMessageRepository,
    DjangoConversationRepository,
    DjangoUserRepository,
    DjangoDataSetRepository,
    DjangoDocumentChunkRepository,
    DjangoProductRepository,
)
from ..injectors import (
    BaseDocumentRetriever,
    DjangoDocumentRetriever,
    BaseProductRetriever,
    DjangoProductRetriever,
    BaseInjector,
)


@dataclass
class EmbeddingsRegistryConfig:
    registry_class: Type[BaseEmbeddingProviderRegistry] = BaseDjangoSettingsEmbeddingRegistry
    providers: Optional[dict[str, str]] = None


@dataclass
class LLMRegistryConfig:
    registry_class: Type[BaseLanguageModelRegistry] = BaseDjangoSettingsModelRegistry
    providers: Optional[dict[str, str]] = None


@dataclass
class RegistryConfig:
    llm: LLMRegistryConfig = field(default_factory=LLMRegistryConfig)
    embeddings: EmbeddingsRegistryConfig = field(default_factory=EmbeddingsRegistryConfig)


@dataclass
class LLMConfig:
    model_class: Type[BaseLLM] = BaseLLM
    callbacks: list[BaseCallbackHandler] = None
    streaming: bool = False


@dataclass
class RepositoryConfig:
    model: models.Model
    repo_class: BaseRepository


@dataclass
class RepositoriesConfig:
    user: BaseUserRepository = DjangoUserRepository
    message: BaseMessageRepository = DjangoMessageRepository
    conversation: BaseConversationRepository = DjangoConversationRepository
    data_set: BaseDataSetRepository = DjangoDataSetRepository
    document_chunk: BaseDocumentChunkRepository = DjangoDocumentChunkRepository
    product: BaseProductRepository = DjangoProductRepository


@dataclass
class LLMToolConfig:
    model_class: Type[BaseLLMTool]
    data_set_id: int
    llm: BaseLanguageModel | None = None


@dataclass
class AgentToolConfig:
    model_class: Type[BaseAgentTool]
    agent_executor: AgentExecutor


@dataclass
class DocumentRetrieverConfig:
    retriever_class: Type[BaseDocumentRetriever] = DjangoDocumentRetriever
    max_documents: int = 12


@dataclass
class ProductRetrieverConfig:
    retriever_class: Type[BaseProductRetriever] = DjangoProductRetriever
    number_of_products: int = 12
    max_sample_products: int = 12
    prompt_template: str | None = None
    llm: BaseLanguageModel | None = None


@dataclass
class RetrieversConfig:
    document: DocumentRetrieverConfig = field(default_factory=DocumentRetrieverConfig)
    product: ProductRetrieverConfig = field(default_factory=ProductRetrieverConfig)


@dataclass
class AgentConfig:
    data_set_id: int
    prompt_template: str
    agent_class: Type[BaseAgent]
    conversation_service: Type[ConversationService]
    function_tools: Optional[list[Type[BaseFunctionTool]]] = None
    llm_tools: Optional[list[LLMToolConfig]] = None
    agent_tools: Optional[list[AgentToolConfig]] = None
    registry: RegistryConfig = field(default_factory=RegistryConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    repositories: RepositoriesConfig = field(default_factory=RepositoriesConfig)
    retrievers: RetrieversConfig = field(default_factory=RetrieversConfig)
    injector: Type[BaseInjector] | None = BaseInjector


@dataclass
class ToolCallingAgentConfig(AgentConfig):
    prompt_template: Sequence[MessageLikeRepresentation]
