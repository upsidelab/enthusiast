from typing import Any

from enthusiast_common.repositories import BaseConversationRepository
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
            type=message.type, text=message.content, function_name=getattr(message, "name", None)
        )

    @property
    def messages(self) -> list[BaseMessage]:
        messages = self._conversation.messages.filter(answer_failed=False).order_by("created_at")
        message_dicts = [
            {"type": message.langchain_type, "data": {"content": message.text, "name": message.function_name}}
            for message in messages
        ]
        return messages_from_dict(message_dicts)

    def clear(self) -> None:
        self._conversation.messages.all().delete()
