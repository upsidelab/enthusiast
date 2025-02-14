import logging

from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import SystemMessage

from catalog.language_models import LanguageModelRegistry
from catalog.models import DataSet
from agent.tools.manager import ToolManager

from agent.callbacks import WebSocketCallbackHandler

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, data_set: DataSet, messages: list, conversation_id: int):
        logger.debug("Initialize Agent")
        callback_handler = WebSocketCallbackHandler(f"conversation_{conversation_id}")
        self._llm = (
            LanguageModelRegistry()
            .provider_for_dataset(data_set)
            .provide_language_model(callbacks=[callback_handler])
        )

        self._tools = ToolManager(data_set=data_set, chat_model=self._llm.model_name).tools
        self._system_message = SystemMessage(
            "You are an agent that knows everything about company\'s product catalog and content")
        self._agent = create_conversational_retrieval_agent(
            llm=self._llm,
            tools=self._tools,
            system_message=self._system_message,
            verbose=True
        )
        # Populate memory with history of conversation.
        logger.debug(f"Populate memory. Number of messages in conversation history: {len(messages)}")
        self._populate_agent_memory(messages)

    def _populate_agent_memory(self, messages):
        self._agent.memory = ConversationSummaryBufferMemory(llm=self._llm,
                                                             memory_key="chat_history",
                                                             return_messages=True,
                                                             max_token=3000,
                                                             output_key="output")
        # Populate memory, filter out unwanted messages.
        self._agent.memory.chat_memory.add_messages(messages)

    def process_user_request(self, prompt: str):
        return self._agent.invoke({"input": prompt})
