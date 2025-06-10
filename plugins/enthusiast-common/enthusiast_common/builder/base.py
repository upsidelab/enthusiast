from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatMessagePromptTemplate
from langchain_core.tools import BaseTool

from ..agents import BaseAgent
from ..config import AgentConfig, LLMConfig
from .validator import AgentConfigValidator
from ..injectors import BaseProductRetriever, BaseDocumentRetriever, BaseInjector
from ..tools import BaseAgentTool, BaseLLMTool, BaseFunctionTool
from ..registry import BaseLanguageModelRegistry, BaseEmbeddingProviderRegistry, BaseDBModelsRegistry
from ..repositories import (
    BaseProductRepository,
    BaseDataSetRepository,
    BaseDocumentChunkRepository,
    BaseUserRepository,
    BaseMessageRepository,
    BaseConversationRepository,
)
from ..services import BaseConversationService


@dataclass
class RepositoriesInstances:
    user: BaseUserRepository
    message: BaseMessageRepository
    conversation: BaseConversationRepository
    data_set: BaseDataSetRepository
    document_chunk: BaseDocumentChunkRepository
    product: BaseProductRepository


class BaseAgentBuilder(ABC):
    _repositories: RepositoriesInstances

    def __init__(self, config: AgentConfig):
        self._data_set_id = None
        self.validator = AgentConfigValidator()
        self.validator.validate_or_raise(config)
        self._config = config

    def build(self) -> BaseAgent:
        model_registry = self._build_db_models_registry()
        self._build_and_set_repositories(model_registry)
        self._data_set_id = self._repositories.conversation.get_data_set_id(self._config.conversation_id)
        llm = self._build_llm(self._config.llm)
        conversation_service = self._build_conversation_service()
        embeddings_registry = self._build_embeddings_registry()
        injector = self._build_injector(embeddings_registry)
        tools = self._build_tools(default_llm=llm, injector=injector)
        return self._build_agent(tools, llm, self._config.prompt_template, conversation_service)

    @abstractmethod
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: BaseConversationService,
    ) -> BaseAgent:
        pass

    @abstractmethod
    def _build_injector(self, embeddings_registry: BaseEmbeddingProviderRegistry) -> BaseInjector:
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
    def _build_product_retriever(self) -> BaseProductRetriever:
        pass

    @abstractmethod
    def _build_document_retriever(self, embeddings_registry: BaseEmbeddingProviderRegistry) -> BaseDocumentRetriever:
        pass
