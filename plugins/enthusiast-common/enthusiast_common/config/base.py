from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from ..agents import BaseAgent
from ..injectors.base import BaseInjector
from ..llm import BaseLLM
from ..registry import (
    BaseDBModelsRegistry,
    BaseEmbeddingProviderRegistry,
    BaseLanguageModelRegistry,
)
from ..repositories.base import (
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseUserRepository,
)
from ..retrievers import BaseRetriever
from ..services.conversation import BaseConversationService
from ..tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool

InjectorT = TypeVar("InjectorT", bound=BaseInjector)


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
    document_chunk: Type[BaseModelChunkRepository]
    product: Type[BaseProductRepository]
    product_chunk: Type[BaseModelChunkRepository]


@dataclass
class LLMToolConfig:
    model_class: Type[BaseLLMTool]
    data_set_id: int | None = None
    llm: BaseLanguageModel | None = None


@dataclass
class AgentToolConfig:
    model_class: Type[BaseAgentTool]
    agent: BaseAgent


@dataclass
class RetrieverConfig:
    retriever_class: Type[BaseRetriever]
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrieversConfig:
    document: RetrieverConfig
    product: RetrieverConfig


@dataclass
class AgentConfig(Generic[InjectorT]):
    conversation_id: int
    prompt_template: PromptTemplate | ChatPromptTemplate
    agent_class: Type[BaseAgent]
    conversation_service: Type[BaseConversationService]
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[InjectorT]
    registry: RegistryConfig
    function_tools: Optional[list[Type[BaseFunctionTool]]] = None
    llm_tools: Optional[list[LLMToolConfig]] = None
    agent_tools: Optional[list[AgentToolConfig]] = None
    llm: LLMConfig = field(default_factory=LLMConfig)


@dataclass
class ToolCallingAgentConfig(AgentConfig):
    prompt_template: ChatPromptTemplate
