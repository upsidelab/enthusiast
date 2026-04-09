from typing import Any, Optional

from enthusiast_common.memory import BaseMemoryCompactor
from enthusiast_common.repositories import BaseConversationRepository
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage

COMPACTION_INTERVAL = 10  # number of human messages between summary generations

_INITIAL_SUMMARIZATION_PROMPT = SystemMessage(
    "You are a helpful assistant. Summarize the conversation below concisely (500 tokens or fewer). "
    "Focus on key facts, decisions, requests, and any important context the user or assistant established. "
    "Write in third person (e.g. 'The user asked...', 'The assistant confirmed...')."
)

_INCREMENTAL_SUMMARIZATION_PROMPT = SystemMessage(
    "You are a helpful assistant. You are given an existing summary of a conversation and a set of new messages "
    "that followed it. Update the summary to incorporate the new information, keeping it concise (500 tokens or fewer). "
    "Write in third person (e.g. 'The user asked...', 'The assistant confirmed...')."
)


class LLMMemoryCompactor(BaseMemoryCompactor):
    """
    Generates and persists an LLM-based summary of the conversation history.

    A new summary is built every COMPACTION_INTERVAL human messages. The summary is
    stored on the Conversation record and injected into subsequent agent calls so that
    context beyond the token-trimming window is not lost.
    """

    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any, llm: BaseLanguageModel):
        self._conversation = conversation_repo.get_by_id(conversation_id)
        self._llm = llm

    def get_summary(self) -> Optional[str]:
        """Return the current persisted summary, or None if one has not been generated yet."""
        return self._conversation.conversation_summary or None

    def compact_if_needed(self, messages: list) -> None:
        """Generate a new summary if COMPACTION_INTERVAL human messages have been added since the last one."""
        human_count = sum(1 for m in messages if isinstance(m, HumanMessage))

        last_count = self._conversation.conversation_summary_human_message_count
        if human_count - last_count < COMPACTION_INTERVAL:
            return

        existing_summary = self._conversation.conversation_summary
        new_messages = self._messages_since_last_compaction(messages, last_count)

        summary = self._generate_summary(new_messages, existing_summary)
        self._conversation.conversation_summary = summary
        self._conversation.conversation_summary_human_message_count = human_count
        self._conversation.save(update_fields=["conversation_summary", "conversation_summary_human_message_count"])

    @staticmethod
    def _messages_since_last_compaction(messages: list, last_human_count: int) -> list:
        """Return only the messages added after the previous compaction point.

        Iterates through the full message list and returns a slice starting at the first
        message after the last_human_count-th HumanMessage. Always called after the
        compaction threshold is confirmed, so a matching slice is guaranteed to exist.
        """
        seen_humans = 0
        for i, m in enumerate(messages):
            if isinstance(m, HumanMessage):
                seen_humans += 1
            if seen_humans > last_human_count:
                return messages[i:]
        return messages

    def _generate_summary(self, new_messages: list, existing_summary: Optional[str]) -> str:
        new_text = "\n".join(
            f"{m.type.upper()}: {m.content}"
            for m in new_messages
            if isinstance(m.content, str)
        )
        if existing_summary:
            content = f"Existing summary:\n{existing_summary}\n\nNew messages:\n{new_text}"
            prompt = _INCREMENTAL_SUMMARIZATION_PROMPT
        else:
            content = new_text
            prompt = _INITIAL_SUMMARIZATION_PROMPT

        response = self._llm.invoke([prompt, HumanMessage(content=content)])
        return response.content
