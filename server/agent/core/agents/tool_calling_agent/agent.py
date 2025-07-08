from enthusiast_common.agents import BaseAgent
from enthusiast_common.tools.base import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

from agent.core.persistent_chat_history import PersistentChatHistory
from agent.core.summary_chat_memory import SummaryChatMemory
from agent.injector import Injector
from agent.repositories import DjangoConversationRepository


class ToolCallingAgent(BaseAgent):
    def __init__(
        self,
        tools: list[BaseTool],
        llm: BaseLanguageModel,
        prompt: ChatPromptTemplate,
        conversation_id: int,
        conversation_repo: DjangoConversationRepository,
        injector: Injector,
        callback_handler: BaseCallbackHandler | None = None,
        **kwargs,
    ):
        self._tools = tools
        self._llm = llm
        self._prompt = prompt
        self._injector = injector
        self._conversation_id = conversation_id
        self._callback_handler = callback_handler
        memory = self._create_agent_memory()
        self._memory = memory
        self._agent_executor = self._create_agent_executor(**kwargs)
        super().__init__(tools=tools, llm=llm, prompt=prompt, conversation_repo=conversation_repo, conversation_id=conversation_id, memory=memory, callback_handler=callback_handler, injector=injector)

    def _create_agent_executor(self, **kwargs):
        tools = self._create_tools()
        agent = create_tool_calling_agent(self._llm, tools, self._prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, memory=self._memory, **kwargs)

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke(
            {"input": input_text}, config={"callbacks": [self._callback_handler] if self._callback_handler else []}
        )
        return agent_output["output"]

    def _create_agent_memory(self) -> SummaryChatMemory:
        conversation = self._injector.repositories.conversation.get_by_id(self._conversation_id)
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
