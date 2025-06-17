from abc import ABC, abstractmethod
from typing import Self

from langchain.agents import AgentExecutor
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from ..services import BaseConversationService


class BaseAgent(ABC):
    _agent_executor: AgentExecutor

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_service: BaseConversationService,
        conversation_id: int,
        agent_executor: AgentExecutor,
        memory: ConversationSummaryBufferMemory,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_service = conversation_service
        self._conversation_id = conversation_id
        self._memory = memory
        self._agent_executor = agent_executor

    @abstractmethod
    def get_answer(self, input_text: str) -> str:
        pass

    @abstractmethod
    def _create_agent_executor(self, **kwargs) -> AgentExecutor:
        pass

    @abstractmethod
    def _create_agent_memory(self, messages) -> ConversationSummaryBufferMemory:
        pass

    def _set_agent_executor(self, agent_executor: AgentExecutor):
        self._agent_executor = agent_executor

    def create(self, **kwargs) -> Self:
        agent_executor = self._create_agent_executor(**kwargs)
        self._set_agent_executor(agent_executor)
        return self
