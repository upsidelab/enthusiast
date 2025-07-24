from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.memory import BaseMemory
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate
from langchain_core.tools import BaseTool

from ..agents import BaseAgent
from ..config import AgentConfig, LLMConfig
from ..injectors import BaseInjector
from ..registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from ..structures import RepositoriesInstances
from ..tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool

ConfigT = TypeVar("ConfigT", bound=AgentConfig)


class BaseAgentBuilder(ABC, Generic[ConfigT]):
    _repositories: RepositoriesInstances

    def __init__(self, config: ConfigT):
        self._llm = None
        self._embeddings_registry = None
        self._data_set_id = None
        self._injector = None
        self._config = config

    def build(self) -> BaseAgent:
        model_registry = self._build_db_models_registry()
        self._build_and_set_repositories(model_registry)
        self._data_set_id = self._repositories.conversation.get_data_set_id(self._config.conversation_id)
        self._llm = self._build_llm(self._config.llm)
        self._embeddings_registry = self._build_embeddings_registry()
        self._injector = self._build_injector()
        tools = self._build_tools(default_llm=self._llm, injector=self._injector)
        agent_callback_handler = self._build_agent_callback_handler()
        return self._build_agent(tools, self._llm, self._config.prompt_template, agent_callback_handler)

    @abstractmethod
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
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
    def _build_agent_callback_handler(self) -> Optional[BaseCallbackHandler]:
        pass

    @abstractmethod
    def _build_llm_callback_handlers(self) -> Optional[BaseCallbackHandler]:
        pass

    @abstractmethod
    def _build_chat_summary_memory(self) -> BaseMemory:
        pass

    @abstractmethod
    def _build_chat_limited_memory(self) -> BaseMemory:
        pass
