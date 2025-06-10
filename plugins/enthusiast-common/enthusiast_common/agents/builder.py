from dataclasses import fields, dataclass

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatMessagePromptTemplate
from langchain_core.tools import BaseTool

from .base import BaseAgent
from ..config import AgentConfig, LLMConfig, AgentConfigValidator
from ..injectors import BaseProductRetriever, BaseDocumentRetriever, BaseInjector
from ..services.conversation import ConversationService
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


@dataclass
class RepositoriesInstances:
    user: BaseUserRepository
    message: BaseMessageRepository
    conversation: BaseConversationRepository
    data_set: BaseDataSetRepository
    document_chunk: BaseDocumentChunkRepository
    product: BaseProductRepository


class AgentBuilder:
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
        prompt = self._build_prompt()
        conversation_service = self._build_conversation_service()
        embeddings_registry = self._build_embeddings_registry()
        injector = self._build_injector(embeddings_registry)
        tools = self._build_tools(default_llm=llm, injector=injector)
        return self._build_agent(tools, llm, prompt, conversation_service)

    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: ConversationService,
    ) -> BaseAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_service=conversation_service,
            conversation_id=self._config.conversation_id,
        )

    def _build_injector(self, embeddings_registry: BaseEmbeddingProviderRegistry) -> BaseInjector:
        injector = self._config.injector()
        document_retriever = self._build_document_retriever(embeddings_registry=embeddings_registry)
        product_retriever = self._build_product_retriever()
        injector.document_retriever = document_retriever
        injector.product_retriever = product_retriever
        return injector

    def _build_llm_registry(self) -> BaseLanguageModelRegistry:
        llm_registry_class = self._config.registry.llm.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)
        return llm_registry

    def _build_db_models_registry(self) -> BaseDBModelsRegistry:
        db_models_registry_class = self._config.registry.model.registry_class
        if models_config := self._config.registry.model.models_config:
            db_model_registry = db_models_registry_class(models_config=models_config)
        else:
            db_model_registry = db_models_registry_class()
        return db_model_registry

    def _build_and_set_repositories(self, models_registry: BaseDBModelsRegistry) -> None:
        repositories = {}
        for field in fields(self._config.repositories):
            name = field.name
            repo_class = getattr(self._config.repositories, name)
            model_class = models_registry.get_model_class_by_name(name)
            repositories[name] = repo_class(model_class)
        self._repositories = RepositoriesInstances(**repositories)

    def _build_embeddings_registry(self) -> BaseEmbeddingProviderRegistry:
        embeddings_registry_class = self._config.registry.embeddings.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            embeddings_registry = embeddings_registry_class(providers=providers)
        else:
            embeddings_registry = embeddings_registry_class(data_set_repo=data_set_repo)
        return embeddings_registry

    def _build_llm(self, llm_config: LLMConfig) -> BaseLanguageModel:
        data_set_repo = self._repositories.data_set
        llm_registry = self._build_llm_registry()
        llm = self._config.llm.model_class(
            llm_registry=llm_registry,
            callbacks=llm_config.callbacks,
            streaming=llm_config.streaming,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._data_set_id)

    def _build_default_llm(self) -> BaseLanguageModel:
        llm_registry_class = self._config.registry.llm.registry_class
        data_set_repo = self._repositories.data_set
        if providers := self._config.registry.llm.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)

        llm = self._config.llm.model_class(
            llm_registry=llm_registry,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._data_set_id)

    def _build_prompt(self) -> PromptTemplate | ChatMessagePromptTemplate:
        return self._config.agent_class.create_prompt(self._config.prompt_template)

    def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
        function_tools = self._build_function_tools() if self._config.function_tools else []
        llm_tools = self._build_llm_tools(default_llm, injector) if self._config.llm_tools else []
        agent_tools = self._build_agent_tools(injector) if self._config.agent_tools else []
        return [*function_tools, *llm_tools, *agent_tools]

    def _build_function_tools(self) -> list[BaseFunctionTool]:
        return [tool() for tool in self._config.function_tools]

    def _build_llm_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseLLMTool]:
        tools = []
        for tool_config in self._config.llm_tools:
            llm = default_llm
            data_set_id = tool_config.data_set_id or self._data_set_id
            if tool_config.llm:
                llm = tool_config.llm
            tools.append(
                tool_config.model_class(
                    data_set_id=data_set_id,
                    data_set_repo=self._repositories.data_set,
                    llm=llm,
                    injector=injector,
                )
            )
        return tools

    def _build_agent_tools(self, injector: BaseInjector | None) -> list[BaseAgentTool]:
        return [
            tool_config.model_class(agent_executor=tool_config.agent_executor, injector=injector)
            for tool_config in self._config.agent_tools
        ]

    def _build_conversation_service(self) -> ConversationService:
        return self._config.conversation_service(
            conversation_repo=self._repositories.conversation,
            message_repo=self._repositories.message,
            user_repo=self._repositories.user,
        )

    def _build_product_retriever(self) -> BaseProductRetriever:
        if config := self._config.retrievers.product.llm:
            llm = self._build_llm(config.llm)
        else:
            llm = self._build_default_llm()
        return self._config.retrievers.product.retriever_class(
            data_set_id=self._data_set_id,
            data_set_repo=self._repositories.data_set,
            product_repo=self._repositories.product,
            prompt_template=self._config.retrievers.product.prompt_template,
            number_of_products=self._config.retrievers.product.number_of_products,
            max_sample_products=self._config.retrievers.product.max_sample_products,
            llm=llm,
        )

    def _build_document_retriever(self, embeddings_registry: BaseEmbeddingProviderRegistry) -> BaseDocumentRetriever:
        return self._config.retrievers.document.retriever_class(
            data_set_id=self._data_set_id,
            data_set_repo=self._repositories.data_set,
            embeddings_registry=embeddings_registry,
            max_documents=self._config.retrievers.document.max_documents,
            document_chunk_repo=self._repositories.document_chunk,
        )
