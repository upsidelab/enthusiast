from typing import Type, Optional

from langchain.agents import AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass, field

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate

from ..agents import BaseAgent
from ..services.conversation import BaseConversationService
from ..tools import BaseAgentTool, BaseLLMTool, BaseFunctionTool
from ..llm import BaseLLM
from ..registry import (
    BaseLanguageModelRegistry,
    BaseEmbeddingProviderRegistry,
    BaseDBModelsRegistry,
)
from ..repositories.base import (
    BaseUserRepository,
    BaseMessageRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseProductRepository,
    BaseDocumentChunkRepository,
)
from ..injectors import (
    BaseDocumentRetriever,
    BaseProductRetriever,
    BaseInjector,
)


@dataclass
class EmbeddingsRegistryConfig:
    registry_class: Type[BaseEmbeddingProviderRegistry]
    providers: Optional[dict[str, str]] = None


@dataclass
class LLMRegistryConfig:
    registry_class: Type[BaseLanguageModelRegistry]
    providers: Optional[dict[str, str]] = None


@dataclass
class ModelsRegistryConfig:
    registry_class: Type[BaseDBModelsRegistry]
    models_config: Optional[dict[str, str]] = None


@dataclass
class RegistryConfig:
    llm: LLMRegistryConfig
    embeddings: EmbeddingsRegistryConfig
    model: ModelsRegistryConfig


@dataclass
class LLMConfig:
    model_class: Type[BaseLLM] = field(default=BaseLLM)
    callbacks: list[BaseCallbackHandler] = None
    streaming: bool = False


@dataclass
class RepositoriesConfig:
    user: Type[BaseUserRepository]
    message: Type[BaseMessageRepository]
    conversation: Type[BaseConversationRepository]
    data_set: Type[BaseDataSetRepository]
    document_chunk: Type[BaseDocumentChunkRepository]
    product: Type[BaseProductRepository]


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
    retriever_class: Type[BaseDocumentRetriever]
    max_documents: int = 12


@dataclass
class ProductRetrieverConfig:
    retriever_class: Type[BaseProductRetriever]
    number_of_products: int = 12
    max_sample_products: int = 12
    prompt_template: str | None = None
    llm: BaseLanguageModel | None = None


@dataclass
class RetrieversConfig:
    document: DocumentRetrieverConfig
    product: ProductRetrieverConfig


@dataclass
class AgentConfig:
    conversation_id: int
    prompt_template: PromptTemplate | ChatMessagePromptTemplate
    agent_class: Type[BaseAgent]
    conversation_service: Type[BaseConversationService]
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[BaseInjector]
    registry: RegistryConfig
    function_tools: Optional[list[Type[BaseFunctionTool]]] = None
    llm_tools: Optional[list[LLMToolConfig]] = None
    agent_tools: Optional[list[AgentToolConfig]] = None
    llm: LLMConfig = field(default_factory=LLMConfig)


@dataclass
class ToolCallingAgentConfig(AgentConfig):
    prompt_template: ChatMessagePromptTemplate
