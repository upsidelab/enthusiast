from typing import Type, Optional, Sequence

from django.db import models
from langchain.agents import AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass

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
    BaseRepository,
)
from ..repositories.django import (
    DjangoMessageRepository,
    DjangoConversationRepository,
    DjangoUserRepository,
    DjangoDataSetRepository,
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
    llm: LLMRegistryConfig = LLMRegistryConfig()
    embeddings: EmbeddingsRegistryConfig = EmbeddingsRegistryConfig()


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
class AgentConfig:
    data_set_id: int
    prompt_template: str
    agent_class: Type[BaseAgent]
    conversation_service: Type[ConversationService]
    function_tools: Optional[list[Type[BaseFunctionTool]]] = None
    llm_tools: Optional[list[LLMToolConfig]] = None
    agent_tools: Optional[list[AgentToolConfig]] = None
    registry: RegistryConfig = RegistryConfig()
    llm: LLMConfig = LLMConfig()
    repositories: RepositoriesConfig = RepositoriesConfig()
    # injectors


@dataclass
class ToolCallingAgentConfig(AgentConfig):
    prompt_template = Sequence[MessageLikeRepresentation]
