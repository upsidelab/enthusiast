from typing import Any, Generic, Optional, Type, TypeVar

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.memory import BaseMemory
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from pydantic import BaseModel, ConfigDict, Field

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
from ..tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool

InjectorT = TypeVar("InjectorT", bound=BaseInjector)


class ArbitraryTypeBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EmbeddingsRegistryConfig(ArbitraryTypeBaseModel):
    registry_class: Type[BaseEmbeddingProviderRegistry]
    providers: Optional[dict[str, str]] = None


class LLMRegistryConfig(ArbitraryTypeBaseModel):
    registry_class: Type[BaseLanguageModelRegistry]
    providers: Optional[dict[str, str]] = None


class ModelsRegistryConfig(ArbitraryTypeBaseModel):
    registry_class: Type[BaseDBModelsRegistry]
    models_config: Optional[dict[str, str]] = None


class RegistryConfig(ArbitraryTypeBaseModel):
    llm: LLMRegistryConfig
    embeddings: EmbeddingsRegistryConfig
    model: ModelsRegistryConfig


class LLMConfig(ArbitraryTypeBaseModel):
    llm_class: Type[BaseLLM] = BaseLLM
    callbacks: Optional[list[BaseCallbackHandler]] = None
    streaming: bool = False


class RepositoriesConfig(ArbitraryTypeBaseModel):
    user: Type[BaseUserRepository]
    message: Type[BaseMessageRepository]
    conversation: Type[BaseConversationRepository]
    data_set: Type[BaseDataSetRepository]
    document_chunk: Type[BaseModelChunkRepository]
    product: Type[BaseProductRepository]
    product_chunk: Type[BaseModelChunkRepository]


class LLMToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseLLMTool]
    data_set_id: Optional[Any] = None
    llm: Optional[BaseLanguageModel] = None


class AgentToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseAgentTool]
    agent: BaseAgent


class RetrieverConfig(ArbitraryTypeBaseModel):
    retriever_class: Type[BaseRetriever]
    extra_kwargs: dict[str, Any] = Field(default_factory=dict)


class RetrieversConfig(ArbitraryTypeBaseModel):
    document: RetrieverConfig
    product: RetrieverConfig


class AgentCallbackHandlerConfig(ArbitraryTypeBaseModel):
    handler_class: Type[BaseCallbackHandler]
    args: dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel, Generic[InjectorT]):
    conversation_id: Any
    prompt_template: PromptTemplate | ChatPromptTemplate
    agent_class: Type[BaseAgent]
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[InjectorT]
    registry: RegistryConfig
    function_tools: Optional[list[Type[BaseFunctionTool]]] = None
    llm_tools: Optional[list[LLMToolConfig]] = None
    agent_tools: Optional[list[AgentToolConfig]] = None
    agent_callback_handler: Optional[AgentCallbackHandlerConfig] = None
    llm: LLMConfig = Field(default_factory=LLMConfig)


class ToolCallingAgentConfig(AgentConfig):
    prompt_template: ChatPromptTemplate
