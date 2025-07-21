from abc import ABC
from typing import Any

from enthusiast_common.agents import BaseAgent
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.memory import BaseMemory
from langchain_core.tools import BaseTool, render_text_description_and_args

from .structured_re_act_output_parser import StructuredReActOutputParser


class BaseReActAgent(BaseAgent, ABC):
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
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=StructuredReActOutputParser(),
        )
        return AgentExecutor(agent=agent, tools=tools, memory=self._build_memory())
