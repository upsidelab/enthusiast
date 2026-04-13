from typing import Any, Optional

from enthusiast_common.memory import BaseMemoryCompactor
from enthusiast_common.repositories import BaseConversationRepository
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agent.core.memory.persistent_chat_history import PersistentChatHistory

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

    A new summary is built every COMPACTION_INTERVAL human messages since the last compaction.
    The summary is stored on the Conversation record and injected into subsequent agent calls
    so that context beyond the token-trimming window is not lost.
    """

    def __init__(
        self,
        conversation_repo: BaseConversationRepository,
        conversation_id: Any,
        llm: BaseLanguageModel,
        chat_history: PersistentChatHistory,
    ):
        self._conversation = conversation_repo.get_by_id(conversation_id)
        self._llm = llm
        self._chat_history = chat_history

    def get_summary(self) -> Optional[str]:
        """Return the current persisted summary, or None if one has not been generated yet."""
        return self._conversation.conversation_summary or None

    def compact_if_needed(self) -> None:
        """Generate a new summary if COMPACTION_INTERVAL human messages have been added since the last one."""
        last_summarized_message_id = self._conversation.last_summarized_message_id
        result = self._chat_history.messages_after(last_summarized_message_id)

        if not result.messages:
            return

        human_messages_count = sum(1 for m in result.messages if isinstance(m, HumanMessage))
        if human_messages_count < COMPACTION_INTERVAL:
            return

        summary = self._generate_summary(result.messages, self._conversation.conversation_summary)
        self._conversation.conversation_summary = summary
        self._conversation.last_summarized_message_id = result.last_message_id
        self._conversation.save(update_fields=["conversation_summary", "last_summarized_message_id"])

    def _generate_summary(self, new_messages: list[BaseMessage], existing_summary: Optional[str]) -> str:
        if existing_summary:
            prompt_messages = [
                _INCREMENTAL_SUMMARIZATION_PROMPT,
                HumanMessage(content=f"Existing summary:\n{existing_summary}"),
            ] + new_messages
        else:
            prompt_messages = [_INITIAL_SUMMARIZATION_PROMPT] + new_messages

        response = self._llm.invoke(prompt_messages)
        return response.content
