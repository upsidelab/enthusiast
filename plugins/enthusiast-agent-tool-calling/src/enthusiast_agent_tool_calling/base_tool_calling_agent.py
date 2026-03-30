from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory

from enthusiast_common.agents import BaseAgent
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, trim_messages, BaseMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.tools import BaseTool

MAX_HISTORY_TOKENS = 3000


class BaseToolCallingAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history

        agent = self._build_agent()
        input_messages = self._build_limited_history(history) + [HumanMessage(content=input_text)]
        result = agent.invoke({ "messages": input_messages }, config=self._build_invoke_config())

        new_messages = result["messages"][len(input_messages):]
        final_message = next(
            m for m in reversed(new_messages)
            if isinstance(m, AIMessage) and not m.tool_calls
        )

        self._persist_turn(history, input_text, new_messages)
        return final_message.text()

    def _build_limited_history(self, history: BaseChatMessageHistory) -> list[BaseMessage]:
        return trim_messages(
            history.messages,
            strategy="last",
            token_counter=self._llm,
            max_tokens=MAX_HISTORY_TOKENS,
            start_on=HumanMessage,
            include_system=True,
            allow_partial=False,
        )

    def _persist_turn(self, history: BaseChatMessageHistory, input_text: str, new_messages: list) -> None:
        """Persist one conversation turn to history in the correct storage order.

        AIMessages that contain multiple tool calls are split into individual
        INTERMEDIATE_STEP records, each paired immediately with its FUNCTION result,
        so that the 1:1 INTERMEDIATE_STEP → FUNCTION pairing invariant is maintained.
        """
        tool_results = {msg.tool_call_id: msg for msg in new_messages if isinstance(msg, ToolMessage)}

        history.add_message(HumanMessage(content=input_text))
        for msg in new_messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    history.add_message(AIMessage(content="", tool_calls=[tool_call]))
                    result_msg = tool_results.get(tool_call["id"])
                    if result_msg:
                        history.add_message(result_msg)
            elif isinstance(msg, ToolMessage):
                pass  # already written inline above
            else:
                history.add_message(msg)

    def _build_tools(self) -> list[BaseTool]:
        return [tool.as_tool() for tool in self._tools]

    def _get_system_prompt(self) -> str | None:
        """Extract the static system prompt text from the configured ChatPromptTemplate."""
        for msg_template in self._prompt.messages:
            if isinstance(msg_template, SystemMessagePromptTemplate):
                formatted = msg_template.format()
                content = formatted.content
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    return " ".join(
                        item["text"] if isinstance(item, dict) and "text" in item else str(item)
                        for item in content
                    )
        return None

    def _build_invoke_config(self) -> dict[str, Any]:
        if self._callback_handler:
            return {"callbacks": [self._callback_handler]}

        return {}

    def _build_agent(self):
        return create_agent(
            model=self._llm,
            tools=self._build_tools(),
            system_prompt=self._get_system_prompt(),
        )
