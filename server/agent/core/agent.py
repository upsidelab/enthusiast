import logging

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from agent.models import Conversation
from agent.tools.manager import ToolManager
from catalog.language_models import LanguageModelRegistry

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, conversation: Conversation):
        data_set = conversation.data_set
        language_model_provider = LanguageModelRegistry().provider_for_dataset(conversation.data_set)

        self._llm = language_model_provider.provide_language_model()
        self._tools = ToolManager(data_set=data_set, language_model_provider=language_model_provider).tools
        self._agent_executor = self._create_agent_with_tools(self._llm, self._tools, data_set.system_message)
        self._memory = self._create_agent_memory(conversation.get_messages())

    def _create_agent_with_tools(self, llm: BaseLanguageModel, tools: list[BaseTool], system_prompt: str):
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(llm, tools, chat_prompt_template)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

    def _create_agent_memory(self, messages):
        memory = ConversationSummaryBufferMemory(
            llm=self._llm, memory_key="chat_history", return_messages=True, max_token_limit=3000, output_key="output"
        )
        memory.chat_memory.add_messages(messages)
        return memory

    def process_user_request(self, prompt: str):
        return self._agent_executor.invoke({"input": prompt, "chat_history": self._memory.buffer})
