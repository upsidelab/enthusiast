import logging

from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import SystemMessage

from catalog.language_models import LanguageModelRegistry
from agent.tools.manager import ToolManager
from agent.models import Conversation

from agent.callbacks import ConversationWebSocketCallbackHandler

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, conversation: Conversation):
        logger.debug("Initialize Agent")
        callback_handler = ConversationWebSocketCallbackHandler(conversation)
        language_model_provider = LanguageModelRegistry().provider_for_dataset(conversation.data_set)
        self._llm = language_model_provider.provide_language_model(callbacks=[callback_handler])
        self._tools = ToolManager(language_model_provider=language_model_provider, conversation=conversation).tools
        self._system_message = SystemMessage(
            "You are a sales support agent, and you know everything about a company and their products.")
        self._agent = create_conversational_retrieval_agent(
            llm=self._llm,
            tools=self._tools,
            system_message=self._system_message,
            verbose=True
        )
        # Populate memory with history of conversation.
        logger.debug(f"Populate memory. Number of messages in conversation history: {len(conversation.get_messages())}")
        self._populate_agent_memory(conversation.get_messages())

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
