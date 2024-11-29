import logging

from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import SystemMessage

from ecl.models import DataSet, EmbeddingModel, EmbeddingDimension
from agent.core.llm_provider import LlmProvider
from agent.tools import CreateAnswerTool


logger = logging.getLogger(__name__)


class Agent:
    def __init__(self,
                 data_set: DataSet,
                 embedding_model: EmbeddingModel,
                 embedding_dimensions: EmbeddingDimension,
                 messages: list  # History of conversation (if we continue existing one).
        ):
        logger.debug("Initialize Agent")
        self._llm = LlmProvider.provide_llm_instance()
        self._tools = [CreateAnswerTool(
            data_set=data_set,
            embedding_model=embedding_model,
            embedding_dimensions=embedding_dimensions,
            chat_model=self._llm.model_name
        )]
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
