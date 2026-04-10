from typing import Any, Optional

from enthusiast_common.agents import BaseAgent
from enthusiast_common.memory import BaseMemoryCompactor
from langchain.agents import create_agent
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, trim_messages
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph

MAX_HISTORY_TOKENS = 3000


class BaseToolCallingAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history
        compactor = self._injector.memory_compactor

        agent = self._build_agent()
        context_messages = self._build_context_messages(history, compactor)
        input_messages = context_messages + [HumanMessage(content=input_text)]
        result = agent.invoke({"messages": input_messages}, config=self._build_invoke_config())

        new_messages = result["messages"][len(context_messages):]
        final_message = next(
            m for m in reversed(new_messages)
            if isinstance(m, AIMessage) and not m.tool_calls
        )

        history.add_messages(new_messages)

        if compactor:
            compactor.compact_if_needed(history.messages)

        return final_message.text

    def _build_context_messages(self, history: BaseChatMessageHistory, compactor: Optional[BaseMemoryCompactor]) -> list[BaseMessage]:
        limited = trim_messages(
            history.messages,
            strategy="last",
            token_counter='approximate',
            max_tokens=MAX_HISTORY_TOKENS,
            start_on=HumanMessage,
            include_system=True,
            allow_partial=False,
        )
        summary_message = self._build_summary_message(compactor)
        if summary_message is not None:
            return [summary_message] + limited
        return limited

    @staticmethod
    def _build_summary_message(compactor: Optional[BaseMemoryCompactor]) -> Optional[SystemMessage]:
        if compactor is None:
            return None
        summary = compactor.get_summary()
        if summary is None:
            return None
        return SystemMessage(content=f"Summary of earlier conversation:\n{summary}")

    def _build_tools(self) -> list[BaseTool]:
        return [tool.as_tool() for tool in self._tools]

    def _get_system_prompt(self) -> str:
        return self._system_prompt.format(**self._get_system_prompt_variables())

    def _build_invoke_config(self) -> dict[str, Any]:
        if self._callback_handler:
            return {"callbacks": [self._callback_handler]}

        return {}

    def _build_agent(self) -> CompiledStateGraph:
        return create_agent(
            model=self._llm,
            tools=self._build_tools(),
            system_prompt=self._get_system_prompt(),
        )
