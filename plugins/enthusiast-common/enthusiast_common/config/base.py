from __future__ import annotations

from typing import Any, Generic, Optional, Type, TypeVar

from langchain_core.callbacks import BaseCallbackHandler
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
    BaseAgentRepository,
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseUserRepository,
)
from ..retrievers import BaseRetriever
from ..tools import BaseAgentTool, BaseFileTool, BaseFunctionTool, BaseLLMTool
from .prompts import ChatPromptTemplateConfig

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


class CallbackHandlerConfig(ArbitraryTypeBaseModel):
    handler_class: Type[BaseCallbackHandler]


class LLMConfig(ArbitraryTypeBaseModel):
    llm_class: Type[BaseLLM] = BaseLLM
    callbacks: Optional[list[CallbackHandlerConfig]] = None


class RepositoriesConfig(ArbitraryTypeBaseModel):
    user: Type[BaseUserRepository]
    message: Type[BaseMessageRepository]
    conversation: Type[BaseConversationRepository]
    data_set: Type[BaseDataSetRepository]
    document_chunk: Type[BaseModelChunkRepository]
    product: Type[BaseProductRepository]
    product_chunk: Type[BaseModelChunkRepository]
    agent: Type[BaseAgentRepository]


class FunctionToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseFunctionTool]


class LLMToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseLLMTool]
    llm: Optional[LLMConfig] = None


class FileToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseFileTool]
    llm: Optional[LLMConfig] = None


class AgentToolConfig(ArbitraryTypeBaseModel):
    tool_class: Type[BaseAgentTool]
    agent: AgentConfig


class RetrieverConfig(ArbitraryTypeBaseModel):
    retriever_class: Type[BaseRetriever]
    extra_kwargs: dict[str, Any] = Field(default_factory=dict)


class RetrieversConfig(ArbitraryTypeBaseModel):
    document: RetrieverConfig
    product: RetrieverConfig


class AgentCallbackHandlerConfig(ArbitraryTypeBaseModel):
    handler_class: Type[BaseCallbackHandler]


class AgentConfig(ArbitraryTypeBaseModel, Generic[InjectorT]):
    agent_class: Type[BaseAgent]
    llm: LLMConfig
    repositories: RepositoriesConfig
    retrievers: RetrieversConfig
    injector: Type[InjectorT]
    registry: RegistryConfig
    chat_prompt_template: ChatPromptTemplateConfig
    tools: Optional[list[FunctionToolConfig | LLMToolConfig | AgentToolConfig | FileToolConfig]] = None
    agent_callback_handler: Optional[AgentCallbackHandlerConfig] = None


class AgentConfigWithDefaults(AgentConfig, Generic[InjectorT]):
    repositories: Optional[RepositoriesConfig] = None
    retrievers: Optional[RetrieversConfig] = None
    injector: Optional[Type[InjectorT]] = None
    registry: Optional[RegistryConfig] = None
    llm: Optional[LLMConfig] = None
