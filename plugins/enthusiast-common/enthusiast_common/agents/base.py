from abc import ABC, abstractmethod
from typing import Sequence, Self

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.chat import MessageLikeRepresentation
from langchain_core.tools import BaseTool

from ..services import ConversationService


class BaseAgent(ABC):
    _agent_executor: AgentExecutor

    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_service: ConversationService,
        conversation_id: int,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_service = conversation_service
        self._conversation_id = conversation_id
        self._memory = self._create_agent_memory(conversation_service.get_messages(self._conversation_id))

    @classmethod
    @abstractmethod
    def create_prompt(cls, template: Sequence[MessageLikeRepresentation] | str) -> PromptTemplate | ChatPromptTemplate:
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


class ToolCallingAgent(BaseAgent):
    def _create_agent_executor(self, **kwargs):
        agent = create_tool_calling_agent(self._llm, self._tools, self._prompt)
        return AgentExecutor(agent=agent, tools=self._tools, verbose=True, **kwargs)

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke({"input": input_text, "chat_history": self._memory.buffer})
        return agent_output["output"]

    @classmethod
    def create_prompt(cls, template: Sequence[MessageLikeRepresentation]) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(template)

    def _create_agent_memory(self, messages) -> ConversationSummaryBufferMemory:
        memory = ConversationSummaryBufferMemory(
            llm=self._llm, memory_key="chat_history", return_messages=True, max_token_limit=3000, output_key="output"
        )
        memory.chat_memory.add_messages(messages)
        return memory
