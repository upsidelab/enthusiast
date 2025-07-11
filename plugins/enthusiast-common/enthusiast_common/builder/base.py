from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import NoneType
from typing import Generic, TypeVar

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate
from langchain_core.tools import BaseTool

from ..agents import BaseAgent
from ..config import AgentConfig, LLMConfig
from ..injectors import BaseInjector
from ..registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from ..repositories import (
    BaseConversationRepository,
    BaseDataSetRepository,
    BaseMessageRepository,
    BaseModelChunkRepository,
    BaseProductRepository,
    BaseUserRepository,
)
from ..services import BaseConversationService
from ..tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool


@dataclass
class RepositoriesInstances:
    user: BaseUserRepository
    message: BaseMessageRepository
    conversation: BaseConversationRepository
    data_set: BaseDataSetRepository
    document_chunk: BaseModelChunkRepository
    product: BaseProductRepository
    product_chunk: BaseModelChunkRepository


ConfigT = TypeVar("ConfigT", bound=AgentConfig)


class BaseAgentBuilder(ABC, Generic[ConfigT]):
    _repositories: RepositoriesInstances

    def __init__(self, config: ConfigT):
        self._llm = None
        self._embeddings_registry = None
        self._data_set_id = None
        self._config = config

    def build(self) -> BaseAgent:
        model_registry = self._build_db_models_registry()
        self._build_and_set_repositories(model_registry)
        self._data_set_id = self._repositories.conversation.get_data_set_id(self._config.conversation_id)
        self._llm = self._build_llm(self._config.llm)
        conversation_service = self._build_conversation_service()
        self._embeddings_registry = self._build_embeddings_registry()
        injector = self._build_injector()
        tools = self._build_tools(default_llm=self._llm, injector=injector)
        agent_callback_handler = self._build_agent_callback_handler()
        return self._build_agent(
            tools, self._llm, self._config.prompt_template, conversation_service, agent_callback_handler
        )

    @abstractmethod
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: BaseConversationService,
        callback_handler: BaseCallbackHandler,
    ) -> BaseAgent:
        pass

    @abstractmethod
    def _build_injector(self) -> BaseInjector:
        pass

    @abstractmethod
    def _build_llm_registry(self) -> BaseLanguageModelRegistry:
        pass

    @abstractmethod
    def _build_db_models_registry(self) -> BaseDBModelsRegistry:
        pass

    @abstractmethod
    def _build_and_set_repositories(self, models_registry: BaseDBModelsRegistry) -> None:
        pass

    @abstractmethod
    def _build_embeddings_registry(self) -> BaseEmbeddingProviderRegistry:
        pass

    @abstractmethod
    def _build_llm(self, llm_config: LLMConfig) -> BaseLanguageModel:
        pass

    @abstractmethod
    def _build_default_llm(self) -> BaseLanguageModel:
        pass

    @abstractmethod
    def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
        pass

    @abstractmethod
    def _build_function_tools(self) -> list[BaseFunctionTool]:
        pass

    @abstractmethod
    def _build_llm_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseLLMTool]:
        pass

    @abstractmethod
    def _build_agent_tools(self) -> list[BaseAgentTool]:
        pass

    @abstractmethod
    def _build_conversation_service(self) -> BaseConversationService:
        pass

    @abstractmethod
    def _build_agent_callback_handler(self) -> list[BaseCallbackHandler | NoneType]:
        pass
