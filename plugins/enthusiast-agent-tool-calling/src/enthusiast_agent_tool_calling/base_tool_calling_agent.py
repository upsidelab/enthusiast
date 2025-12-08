from typing import Any

from enthusiast_common.agents import AgentType, BaseAgent
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.memory import BaseMemory
from langchain_core.tools import BaseTool


class BaseToolCallingAgent(BaseAgent):
    AGENT_TYPE = AgentType.TOOL_CALLING

    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        response = agent_executor.invoke({"input": input_text}, config=self._build_invoke_config())
        return response["output"]

    def _build_tools(self) -> list[BaseTool]:
        return [tool.as_tool() for tool in self._tools]

    def _build_memory(self) -> BaseMemory:
        return self._injector.chat_limited_memory

    def _build_invoke_config(self) -> dict[str, Any]:
        if self._callback_handler:
            return {"callbacks": [self._callback_handler]}

        return {}

    def _build_agent_executor(self) -> AgentExecutor:
        tools = self._build_tools()
        agent = create_tool_calling_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
        )
        return AgentExecutor(
            agent=agent, tools=tools, verbose=True, memory=self._build_memory(), return_intermediate_steps=True
        )
