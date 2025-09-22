from typing import Any

from enthusiast_common.repositories import BaseConversationRepository
from enthusiast_common.structures import LLMFile
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict


class PersistentChatHistory(BaseChatMessageHistory):
    """
    A chat history implementation that persists messages in the database.
    Inject it to agent's memory, to enable conversation persistence.
    """

    def __init__(self, conversation_repo: BaseConversationRepository, conversation_id: Any):
        self._conversation = conversation_repo.get_by_id(conversation_id)

    def add_message(self, message: BaseMessage) -> None:
        self._conversation.messages.create(
            role=message.type, text=message.content, is_file=getattr(message, "is_file", False)
        )

    @property
    def messages(self) -> list[BaseMessage]:
        messages = self._conversation.messages.filter(answer_failed=False, is_file=False).order_by("created_at")
        message_dicts = [{"type": message.role, "data": {"content": message.text}} for message in messages]
        return messages_from_dict(message_dicts)

    def get_files(self) -> list[LLMFile]:
        messages = self._conversation.messages.filter(answer_failed=False, is_file=True).order_by("created_at")
        files = [self._conversation.files.filter(pk=message.parse_file_id()).first() for message in messages]
        return [file.get_llm_file_object() for file in files]

    def clear(self) -> None:
        self._conversation.messages.all().delete()
