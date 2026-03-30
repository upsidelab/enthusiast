from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory

from enthusiast_common.agents import BaseAgent
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, trim_messages, BaseMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.tools import BaseTool

MAX_HISTORY_TOKENS = 3000


class BaseToolCallingAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history

        agent = self._build_agent()
        limited_history = self._build_limited_history(history)
        input_messages = limited_history + [HumanMessage(content=input_text)]
        result = agent.invoke({ "messages": input_messages }, config=self._build_invoke_config())

        new_messages = result["messages"][len(limited_history):]
        final_message = next(
            m for m in reversed(new_messages)
            if isinstance(m, AIMessage) and not m.tool_calls
        )

        history.add_messages(new_messages)
        return final_message.text

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
