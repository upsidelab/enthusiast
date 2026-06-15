from typing import Optional

from enthusiast_common.memory import BaseMemoryCompactor
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, trim_messages


class ContextWindowBuilder:
    """Builds the list of context messages passed to the agent on each invocation.

    Trims history to fit within the token budget and prepends a summary SystemMessage
    when a memory compactor has generated one, so context outside the token window is
    preserved in compressed form.
    """

    def __init__(
        self,
        chat_history: BaseChatMessageHistory,
        memory_compactor: Optional[BaseMemoryCompactor] = None,
    ):
        self._chat_history = chat_history
        self._memory_compactor = memory_compactor

    def build(self, max_tokens: int) -> list[BaseMessage]:
        """Return the trimmed history, optionally preceded by a summary SystemMessage."""
        limited_history = trim_messages(
            self._chat_history.messages,
            strategy="last",
            token_counter="approximate",
            max_tokens=max_tokens,
            start_on=HumanMessage,
            include_system=True,
            allow_partial=False,
        )
        summary_message = self._build_summary_message()
        if summary_message is not None:
            return [summary_message] + limited_history
        return limited_history

    def _build_summary_message(self) -> Optional[SystemMessage]:
        if self._memory_compactor is None:
            return None
        summary = self._memory_compactor.get_summary()
        if summary is None:
            return None
        return SystemMessage(content=f"Summary of earlier conversation:\n{summary}")
