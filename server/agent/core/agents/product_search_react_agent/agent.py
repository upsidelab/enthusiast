import logging

from enthusiast_common.agents import BaseAgent
from enthusiast_common.services import BaseConversationService
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, render_text_description_and_args

from agent.core.agents.product_search_react_agent.output_parser import CustomReactOutputParser
from agent.core.persistent_chat_history import PersistentChatHistory
from agent.core.summary_chat_memory import SummaryChatMemory

logger = logging.getLogger(__name__)


class ProductSearchReActAgent(BaseAgent):
    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_service: BaseConversationService,
        conversation_id: int,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._conversation_service = conversation_service
        self._conversation_id = conversation_id
        memory = self._create_agent_memory()
        self._memory = memory
        self._agent_executor = self._create_agent_executor()
        super().__init__(tools, llm, prompt, conversation_service, conversation_id, memory)

    def _create_agent_executor(self, **kwargs):
        tools = self._create_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=CustomReactOutputParser(),
        )
        return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=self._memory, **kwargs)

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke({"input": input_text, "products_type": "any"})
        return agent_output["output"]

    def _create_agent_memory(self) -> SummaryChatMemory:
        conversation = self._conversation_service.conversation_repo.get_by_id(self._conversation_id)
        history = PersistentChatHistory(conversation)
        memory = SummaryChatMemory(
            llm=self._llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=3000,
            output_key="output",
            chat_memory=history,
        )
        return memory
