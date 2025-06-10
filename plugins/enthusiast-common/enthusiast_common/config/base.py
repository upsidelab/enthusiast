from typing import Type, Optional, Sequence

from django.db import models
from langchain.agents import AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass, field

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.chat import MessageLikeRepresentation

from ..injectors.product import QUERY_PROMPT_TEMPLATE
from ..agents import BaseAgent
from ..services.conversation import ConversationService
from ..tools import BaseAgentTool, BaseLLMTool, BaseFunctionTool
from ..llm import BaseLLM
from ..registry import (
    BaseDjangoSettingsModelRegistry,
    BaseLanguageModelRegistry,
    BaseEmbeddingProviderRegistry,
    BaseDjangoSettingsEmbeddingRegistry,
    BaseDBModelsRegistry,
    BaseDjangoSettingsDBModelRegistry,
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
    Injector,
)


@dataclass
class EmbeddingsRegistryConfig:
    registry_class: Type[BaseEmbeddingProviderRegistry] = field(default=BaseDjangoSettingsEmbeddingRegistry)
    providers: Optional[dict[str, str]] = None


@dataclass
class LLMRegistryConfig:
    registry_class: Type[BaseLanguageModelRegistry] = field(default=BaseDjangoSettingsModelRegistry)
    providers: Optional[dict[str, str]] = None


@dataclass
class ModelsRegistryConfig:
    registry_class: Type[BaseDBModelsRegistry] = field(default=BaseDjangoSettingsDBModelRegistry)
    models_config: Optional[dict[str, str]] = None


@dataclass
class RegistryConfig:
    llm: LLMRegistryConfig = field(default_factory=LLMRegistryConfig)
    embeddings: EmbeddingsRegistryConfig = field(default_factory=EmbeddingsRegistryConfig)
    model: ModelsRegistryConfig = field(default_factory=ModelsRegistryConfig)


@dataclass
class LLMConfig:
    model_class: Type[BaseLLM] = field(default=BaseLLM)
    callbacks: list[BaseCallbackHandler] = None
    streaming: bool = False


@dataclass
class RepositoryConfig:
    model: models.Model
    repo_class: BaseRepository


@dataclass
class RepositoriesConfig:
    user: BaseUserRepository = field(default=DjangoUserRepository)
    message: BaseMessageRepository = field(default=DjangoMessageRepository)
    conversation: BaseConversationRepository = field(default=DjangoConversationRepository)
    data_set: BaseDataSetRepository = field(default=DjangoDataSetRepository)
    document_chunk: BaseDocumentChunkRepository = field(default=DjangoDocumentChunkRepository)
    product: BaseProductRepository = field(default=DjangoProductRepository)


@dataclass
class LLMToolConfig:
    model_class: Type[BaseLLMTool]
    data_set_id: int | None = None
    llm: BaseLanguageModel | None = None


@dataclass
class AgentToolConfig:
    model_class: Type[BaseAgentTool]
    agent_executor: AgentExecutor


@dataclass
class DocumentRetrieverConfig:
    retriever_class: Type[BaseDocumentRetriever] = field(default=DjangoDocumentRetriever)
    max_documents: int = 12


@dataclass
class ProductRetrieverConfig:
    retriever_class: Type[BaseProductRetriever] = field(default=DjangoProductRetriever)
    number_of_products: int = 12
    max_sample_products: int = 12
    prompt_template: str = QUERY_PROMPT_TEMPLATE
    llm: BaseLanguageModel | None = None


@dataclass
class RetrieversConfig:
    document: DocumentRetrieverConfig = field(default_factory=DocumentRetrieverConfig)
    product: ProductRetrieverConfig = field(default_factory=ProductRetrieverConfig)


@dataclass
class AgentConfig:
    conversation_id: int
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
    injector: Type[BaseInjector] = field(default=Injector)


@dataclass
class ToolCallingAgentConfig(AgentConfig):
    prompt_template: Sequence[MessageLikeRepresentation]
