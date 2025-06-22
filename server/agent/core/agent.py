import logging

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from agent.callbacks import ConversationWebSocketCallbackHandler
from agent.core.persistent_chat_history import PersistentChatHistory
from agent.models import Conversation
from agent.tools.manager import ToolManager
from catalog.language_models import LanguageModelRegistry
from .summary_chat_memory import SummaryChatMemory

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, conversation: Conversation, streaming: bool = False):
        callback_handler = ConversationWebSocketCallbackHandler(conversation)
        language_model_provider = LanguageModelRegistry().provider_for_dataset(conversation.data_set)
        self._tools = ToolManager(
            language_model_provider=language_model_provider, conversation=conversation, streaming=streaming
        ).tools

        if streaming:
            self._llm = language_model_provider.provide_streaming_language_model(callbacks=[callback_handler])
        else:
            self._llm = language_model_provider.provide_language_model()

        self._agent_executor = self._create_agent_with_tools(
            self._llm, self._tools, conversation
        )

    def _create_agent_with_tools(self, llm: BaseLanguageModel, tools: list[BaseTool], conversation: Conversation):
        system_prompt = conversation.data_set.system_message
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        memory = self._create_agent_memory(conversation)
        agent = create_tool_calling_agent(llm, tools, chat_prompt_template)
        return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

    def _create_agent_memory(self, conversation: Conversation) -> BaseChatMemory:
        history = PersistentChatHistory(conversation)
        memory = SummaryChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history
        )
        return memory

    def process_user_request(self, prompt: str):
        return self._agent_executor.invoke({"input": prompt})
