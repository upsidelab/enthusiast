from enthusiast_common.agents import BaseAgent
from enthusiast_common.config.base import LLMToolConfig
from enthusiast_common.structures import LLMFile
from langchain.agents import AgentExecutor, create_tool_calling_agent

from agent.core.tools import CreateAnswerTool


class ToolCallingAgent(BaseAgent):
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = [LLMToolConfig(tool_class=CreateAnswerTool)]

    def _build_tools(self):
        return [tool_class.as_tool() for tool_class in self._tools]

    def _build_agent_executor(self, file_objects: list[LLMFile]) -> AgentExecutor:
        tools = self._build_tools()
        prompt = self._create_prompt(file_objects)
        agent = create_tool_calling_agent(self._llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, memory=self._injector.chat_summary_memory)

    def get_answer(self, input_text: str, file_objects: list[LLMFile]) -> str:
        agent_executor = self._build_agent_executor(file_objects)
        response = agent_executor.invoke(
            {"input": input_text, **self._prepare_file_inputs(file_objects)},
            config={"callbacks": [self._callback_handler] if self._callback_handler else []},
        )
        return response["output"]
