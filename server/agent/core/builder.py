from typing import Optional

from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder, RepositoriesInstances
from enthusiast_common.config import AgentConfig, LLMConfig
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from enthusiast_common.services import BaseConversationService
from enthusiast_common.tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate
from langchain_core.tools import BaseTool


class AgentBuilder(BaseAgentBuilder[AgentConfig]):
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: BaseConversationService,
        callback_handler: BaseCallbackHandler,
    ) -> BaseAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_service=conversation_service,
            conversation_id=self._config.conversation_id,
            callback_handler=callback_handler,
        )

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
        for name in self._config.repositories.__class__.model_fields.keys():
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

    def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
        function_tools = self._build_function_tools() if self._config.function_tools else []
        llm_tools = self._build_llm_tools(default_llm, injector) if self._config.llm_tools else []
        agent_tools = self._build_agent_tools() if self._config.agent_tools else []
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

    def _build_agent_tools(self) -> list[BaseAgentTool]:
        return [tool_config.model_class(agent=tool_config.agent) for tool_config in self._config.agent_tools]

    def _build_conversation_service(self) -> BaseConversationService:
        return self._config.conversation_service(
            conversation_repo=self._repositories.conversation,
            message_repo=self._repositories.message,
            user_repo=self._repositories.user,
        )

    def _build_injector(self) -> BaseInjector:
        document_retriever = self._build_document_retriever()
        product_retriever = self._build_product_retriever()
        return self._config.injector(product_retriever=product_retriever, document_retriever=document_retriever)

    def _build_agent_callback_handler(self) -> Optional[BaseCallbackHandler]:
        if self._config.agent_callback_handler:
            return self._config.agent_callback_handler.handler_class(**self._config.agent_callback_handler.args)
        return None

    def _build_document_retriever(self):
        pass

    def _build_product_retriever(self):
        pass
