from abc import ABC, abstractmethod
from typing import Sequence, Self

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.chat import MessageLikeRepresentation

from ..services.conversation import ConversationService
from ..tools import AbstractTool


class BaseAgent(ABC):
    def __init__(
        self,
        tools: list[AbstractTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_service: ConversationService,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_service = conversation_service

    @classmethod
    @abstractmethod
    def create_prompt(cls, template: Sequence[MessageLikeRepresentation] | str) -> PromptTemplate | ChatPromptTemplate:
        pass

    @abstractmethod
    def _create_agent_executor(self, **kwargs) -> AgentExecutor:
        pass

    def _set_agent_executor(self, agent_executor: AgentExecutor):
        self._agent_executor = agent_executor

    def create(self, **kwargs) -> Self:
        self._create_agent_executor(**kwargs)
        self._set_agent_executor(self._agent_executor)
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

        # callback_handler = ConversationWebSocketCallbackHandler(conversation)
        # language_model_provider = LanguageModelRegistry().provider_for_dataset(conversation.data_set)
        # self._tools = ToolManager(
        #     language_model_provider=language_model_provider, conversation=conversation, streaming=streaming
        # ).tools
        #
        # if streaming:
        #     self._llm = language_model_provider.provide_streaming_language_model(callbacks=[callback_handler])
        # else:
        #     self._llm = language_model_provider.provide_language_model()
        #
        # self._agent_executor = self._create_agent_with_tools(
        #     self._llm, self._tools, conversation.data_set.system_message
        # )
        # self._memory = self._create_agent_memory(conversation.get_messages())

    #
    # def _create_agent_memory(self, messages):
    #     memory = ConversationSummaryBufferMemory(
    #         llm=self._llm, memory_key="chat_history", return_messages=True, max_token_limit=3000, output_key="output"
    #     )
    #     memory.chat_memory.add_messages(messages)
    #     return memory
