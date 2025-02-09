import logging

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import SystemMessage

from catalog.language_models import LanguageModelRegistry
from catalog.models import DataSet
from agent.tools.manager import ToolManager

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "You are an agent that knows everything about company\'s product catalog and content"

class Agent:
    def __init__(self, data_set: DataSet, messages: list):
        logger.debug("Initialize Agent")
        language_model_provider = LanguageModelRegistry().provider_for_dataset(data_set)
        self._llm = language_model_provider.provide_language_model()
        self._tools = ToolManager(data_set=data_set, language_model_provider=language_model_provider).tools
        self._system_message = SystemMessage(DEFAULT_SYSTEM_PROMPT)
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        prompt = base_prompt.partial(instructions='You are an agent that knows everything about company\'s product catalog and content')

        self._agent = create_react_agent(self._llm, self._tools, prompt=prompt)
        self._agent_executor = AgentExecutor(agent=self._agent, tools=self._tools, verbose=True)
        # Populate memory with history of conversation.
        # logger.debug(f"Populate memory. Number of messages in conversation history: {len(messages)}")
        # self._populate_agent_memory(messages)

    def _populate_agent_memory(self, messages):
        self._agent.memory = ConversationSummaryBufferMemory(llm=self._llm,
                                                             memory_key="chat_history",
                                                             return_messages=True,
                                                             max_token=3000,
                                                             output_key="output")
        # Populate memory, filter out unwanted messages.
        self._agent.memory.chat_memory.add_messages(messages)

    def process_user_request(self, prompt: str):
        return self._agent_executor.invoke({"input": prompt})
