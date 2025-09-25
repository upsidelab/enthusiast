from enthusiast_common.agents import BaseAgent
from enthusiast_common.config.base import FileToolConfig, LLMToolConfig
from enthusiast_common.structures import LLMFile
from enthusiast_common.tools.files.list_files_tool import FileListTool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from agent.core.tools import CreateAnswerTool


class ToolCallingAgent(BaseAgent):
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = [LLMToolConfig(tool_class=CreateAnswerTool), FileToolConfig(tool_class=FileListTool)]

    def _create_agent_executor(self) -> AgentExecutor:
        tools = self._create_tools()
        agent = create_tool_calling_agent(self._llm, tools, self._prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory)

    def _create_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def get_answer(self, input_text: str, files_objects: list[LLMFile]) -> str:
        agent_executor = self._create_agent_executor()
        agent_output = agent_executor.invoke(
            {"input": input_text},
            config={"callbacks": [self._callback_handler] if self._callback_handler else []},
        )
        return agent_output["output"]
