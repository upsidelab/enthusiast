from enthusiast_common.agents import BaseAgent
from enthusiast_common.tools.base import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

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
        self._agent_executor = self._create_agent_executor(**kwargs)
        super().__init__(tools=tools, llm=llm, prompt=prompt, conversation_repo=conversation_repo, conversation_id=conversation_id, callback_handler=callback_handler, injector=injector)

    def _create_agent_executor(self, **kwargs):
        tools = self._create_tools()
        agent = create_tool_calling_agent(self._llm, tools, self._prompt)
        return AgentExecutor(
            agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory, **kwargs
        )

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke(
            {"input": input_text}, config={"callbacks": [self._callback_handler] if self._callback_handler else []}
        )
        return agent_output["output"]
