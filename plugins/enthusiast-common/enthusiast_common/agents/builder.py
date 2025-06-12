from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatMessagePromptTemplate

from .config import AgentConfig
from ..services.conversation import ConversationService
from ..tools import AbstractTool, BaseAgentTool, BaseLLMTool, BaseFunctionTool
from .base import BaseAgent


class AgentBuilder:
    def __init__(self, config: AgentConfig):
        self._config = config

    def build(self) -> BaseAgent:
        llm = self._build_llm()
        prompt = self._build_prompt()
        tools = self._build_tools(default_llm=llm)
        conversation_service = self._build_conversation_service()
        return self._build_agent(tools, llm, prompt, conversation_service)

    def _build_agent(
        self,
        tools: list[AbstractTool],
        llm: BaseLanguageModel,
        prompt: PromptTemplate | ChatMessagePromptTemplate,
        conversation_service: ConversationService,
    ) -> BaseAgent:
        return self._config.agent_class(tools, llm, prompt, conversation_service)

    def _build_llm(self) -> BaseLanguageModel:
        llm_registry_class = self._config.registry.llm.registry_class
        data_set_repo = self._config.repositories.data_set
        if providers := self._config.registry.llm.providers:
            llm_registry = llm_registry_class(providers=providers)
        else:
            llm_registry = llm_registry_class(data_set_repo=data_set_repo)

        llm = self._config.llm.model_class(
            llm_registry=llm_registry,
            callbacks=self._config.llm.callbacks,
            streaming=self._config.llm.streaming,
            data_set_repo=data_set_repo,
        )
        return llm.create(self._config.data_set_id)

    def _build_prompt(self) -> PromptTemplate | ChatMessagePromptTemplate:
        return self._config.agent_class.create_prompt(self._config.prompt_template)

    def _build_tools(self, default_llm: BaseLanguageModel) -> list[AbstractTool]:
        function_tools = self._build_function_tools() if self._config.function_tools else []
        llm_tools = self._build_llm_tools(default_llm) if self._config.llm_tools else []
        agent_tools = self._build_agent_tools() if self._config.agent_tools else []
        return [*function_tools, *llm_tools, *agent_tools]

    def _build_function_tools(self) -> list[BaseFunctionTool]:
        return [tool() for tool in self._config.function_tools]

    def _build_llm_tools(self, default_llm: BaseLanguageModel) -> list[BaseLLMTool]:
        tools = []
        data_set_repo = self._config.repositories.data_set
        default_data_set = data_set_repo.get_by_id(self._config.data_set_id)

        for tool_config in self._config.llm_tools:
            llm = default_llm
            data_set = default_data_set
            if tool_config.data_set_id:
                data_set = data_set_repo.get_by_id(tool_config.data_set_id)
            if tool_config.llm:
                llm = tool_config.llm
            tools.append(tool_config.model_class(data_set=data_set, llm=llm))
        return tools

    def _build_agent_tools(self) -> list[BaseAgentTool]:
        return [
            tool_config.model_class(agent_executor=tool_config.agent_executor)
            for tool_config in self._config.agent_tools
        ]

    def _build_conversation_service(self) -> ConversationService:
        return self._config.conversation_service(
            conversation_repo=self._config.repositories.conversation,
            message_repo=self._config.repositories.message,
            user_repo=self._config.repositories.user,
        )
