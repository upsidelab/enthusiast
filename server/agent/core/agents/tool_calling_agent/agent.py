from enthusiast_common.agents import BaseAgent
from enthusiast_common.services import BaseConversationService
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool


class ToolCallingAgent(BaseAgent):
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
        memory = self._create_agent_memory(conversation_service.get_messages(self._conversation_id))
        self._memory = memory
        agent_executor = self._create_agent_executor()
        super().__init__(tools, llm, prompt, conversation_service, conversation_id, agent_executor, memory)

    def _create_agent_executor(self, **kwargs):
        agent = create_tool_calling_agent(self._llm, self._tools, self._prompt)
        return AgentExecutor(agent=agent, tools=self._tools, verbose=True, **kwargs)

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke({"input": input_text, "chat_history": self._memory.buffer})
        return agent_output["output"]

    def _create_agent_memory(self, messages) -> ConversationSummaryBufferMemory:
        memory = ConversationSummaryBufferMemory(
            llm=self._llm, memory_key="chat_history", return_messages=True, max_token_limit=3000, output_key="output"
        )
        memory.chat_memory.add_messages(messages)
        return memory
