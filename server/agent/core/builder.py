from typing import Optional

from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder, RepositoriesInstances
from enthusiast_common.callbacks import ConversationCallbackHandler
from enthusiast_common.config.base import AgentConfig, AgentToolConfig, FunctionToolConfig, LLMConfig, LLMToolConfig
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from enthusiast_common.retrievers import BaseRetriever
from enthusiast_common.tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from agent.core.memory import PersistentChatHistory, SummaryChatMemory
from agent.core.memory.limited_chat_memory import LimitedChatMemory


class AgentBuilder(BaseAgentBuilder[AgentConfig]):
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        callback_handler: BaseCallbackHandler,
    ) -> BaseAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=self._config.chat_prompt_template,
            conversation_id=self.conversation_id,
            callback_handler=callback_handler,
            injector=self._injector,
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
        callbacks = self._build_llm_callback_handlers()
        llm = llm_config.llm_class(
            llm_registry=llm_registry,
            callbacks=callbacks,
            streaming=self.streaming,
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

        llm = self._config.llm.llm_class(
            llm_registry=llm_registry,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._data_set_id)

    def _build_tools(self, default_llm: BaseLanguageModel, injector: BaseInjector) -> list[BaseTool]:
        tools = []

        for tool_config in self._config.tools:
            if isinstance(tool_config, FunctionToolConfig):
                tools.append(self._build_function_tool(config=tool_config))
            elif isinstance(tool_config, LLMToolConfig):
                tools.append(self._build_llm_tool(config=tool_config, injector=injector, default_llm=default_llm))
            elif isinstance(tool_config, AgentToolConfig):
                tools.append(self._build_agent_tool(config=tool_config))
            else:
                continue
        return tools

    def _build_function_tool(self, config: FunctionToolConfig) -> BaseFunctionTool:
        return config.tool_class()

    def _build_llm_tool(
        self, config: LLMToolConfig, default_llm: BaseLanguageModel, injector: BaseInjector
    ) -> BaseLLMTool:
        llm = default_llm
        if config.llm:
            llm = config.llm
        return config.tool_class(
            data_set_id=self._data_set_id,
            llm=llm,
            injector=injector,
        )

    def _build_agent_tool(self, config: AgentToolConfig) -> BaseAgentTool:
        builder = self.__init__(config.agent, self.conversation_id, self.streaming)
        agent = builder.build()
        return config.tool_class(agent=agent)

    def _build_injector(self) -> BaseInjector:
        document_retriever = self._build_document_retriever()
        product_retriever = self._build_product_retriever()
        chat_summary_memory = self._build_chat_summary_memory()
        chat_limited_memory = self._build_chat_limited_memory()
        return self._config.injector(
            product_retriever=product_retriever,
            document_retriever=document_retriever,
            repositories=self._repositories,
            chat_summary_memory=chat_summary_memory,
            chat_limited_memory=chat_limited_memory,
        )

    def _build_agent_callback_handler(self) -> Optional[BaseCallbackHandler]:
        if not self._config.agent_callback_handler:
            return None
        if issubclass(self._config.agent_callback_handler.handler_class, ConversationCallbackHandler):
            return self._config.agent_callback_handler.handler_class(conversation_id=self.conversation_id)
        else:
            return self._config.agent_callback_handler.handler_class()

    def _build_llm_callback_handlers(self) -> Optional[list[BaseCallbackHandler]]:
        if not self._config.llm.callbacks:
            return None
        handlers = []
        for config in self._config.llm.callbacks:
            if issubclass(config.handler_class, ConversationCallbackHandler):
                handler = config.handler_class(conversation_id=self.conversation_id)
            else:
                handler = config.handler_class()
            handlers.append(handler)
        return handlers

    def _build_product_retriever(self) -> BaseRetriever:
        llm = self._build_default_llm()
        return self._config.retrievers.product.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=llm,
        )

    def _build_document_retriever(self) -> BaseRetriever:
        return self._config.retrievers.document.retriever_class.create(
            config=self._config,
            data_set_id=self._data_set_id,
            repositories=self._repositories,
            embeddings_registry=self._embeddings_registry,
            llm=self._llm,
        )

    def _build_chat_summary_memory(self) -> SummaryChatMemory:
        history = PersistentChatHistory(self._repositories.conversation, self.conversation_id)
        return SummaryChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )

    def _build_chat_limited_memory(self) -> LimitedChatMemory:
        history = PersistentChatHistory(self._repositories.conversation, self.conversation_id)
        return LimitedChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )
