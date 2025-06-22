from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict

from agent.models import Conversation


class PersistentChatHistory(BaseChatMessageHistory):
    """
    A chat history implementation that persists messages in the database.
    Inject it to agent's memory, to enable conversation persistence.
    """

    def __init__(self, conversation: Conversation):
        self._conversation = conversation

    def add_message(self, message: BaseMessage) -> None:
        self._conversation.messages.create(
            role=message.type,
            text=message.content
        )

    @property
    def messages(self) -> list[BaseMessage]:
        messages = self._conversation.messages.order_by("created_at")
        message_dicts = [
            {"type": message.role, "data": {"content": message.text}}
            for message in messages
        ]
        return messages_from_dict(message_dicts)

    def clear(self) -> None:
        self._conversation.messages.all().delete()
