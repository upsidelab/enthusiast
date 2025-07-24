from typing import Optional

from enthusiast_common.agents import BaseAgent
from enthusiast_common.builder import BaseAgentBuilder, RepositoriesInstances
from enthusiast_common.config import AgentConfig, LLMConfig
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.registry import BaseDBModelsRegistry, BaseEmbeddingProviderRegistry, BaseLanguageModelRegistry
from enthusiast_common.retrievers import BaseRetriever
from enthusiast_common.tools import BaseAgentTool, BaseFunctionTool, BaseLLMTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatMessagePromptTemplate, PromptTemplate
from langchain_core.tools import BaseTool

from agent.core.memory import PersistentChatHistory, SummaryChatMemory
from agent.core.memory.limited_chat_memory import LimitedChatMemory


class AgentBuilder(BaseAgentBuilder[AgentConfig]):
    def _build_agent(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        callback_handler: BaseCallbackHandler,
    ) -> BaseAgent:
        return self._config.agent_class(
            tools=tools,
            llm=llm,
            prompt=prompt,
            conversation_id=self._config.conversation_id,
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
        llm = self._config.llm.llm_class(
            llm_registry=llm_registry,
            callbacks=callbacks,
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

        llm = self._config.llm.llm_class(
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
                tool_config.tool_class(
                    data_set_id=data_set_id,
                    llm=llm,
                    injector=injector,
                )
            )
        return tools

    def _build_agent_tools(self) -> list[BaseAgentTool]:
        return [tool_config.tool_class(agent=tool_config.agent) for tool_config in self._config.agent_tools]

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
        if self._config.agent_callback_handler:
            return self._config.agent_callback_handler.handler_class(**self._config.agent_callback_handler.args)
        return None

    def _build_llm_callback_handlers(self) -> Optional[list[BaseCallbackHandler]]:
        if not self._config.llm.callbacks:
            return None
        handlers = []
        for config in self._config.llm.callbacks:
            if handler_args := config.args:
                handler = config.handler_class(**handler_args)
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
        history = PersistentChatHistory(self._repositories.conversation, self._config.conversation_id)
        return SummaryChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )

    def _build_chat_limited_memory(self) -> LimitedChatMemory:
        history = PersistentChatHistory(self._repositories.conversation, self._config.conversation_id)
        return LimitedChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )
