from datetime import datetime
from typing import Any

from enthusiast_common.services import BaseConversationService
from langchain_core.messages import HumanMessage, AIMessage

from agent.models import Conversation


class ConversationService(BaseConversationService[Conversation]):
    def create_conversation(self, user_id: int, data_set_id: int) -> Conversation:
        user = self.user_repo.get_by_id(user_id)
        data_set = self.user_repo.get_user_dataset(user_id=user_id, data_set_id=data_set_id)
        conversation = self.conversation_repo.create(started_at=datetime.now(), user=user, data_set=data_set)
        return conversation

    def save_user_message(self, conversation_id: int, message: str):
        conversation = self.conversation_repo.get_by_id(conversation_id)
        user_message = self.message_repo.create(
            conversation=conversation,
            created_at=datetime.now(),
            role="user",
            text=message,
        )

        if not conversation.summary:
            self.conversation_repo.update(pk=conversation.id, summary=user_message.text)

    def get_messages(self, conversation_id: int) -> list[Any]:
        """Return list of messages exchanged during a conversation."""
        history = []
        conversation = self.conversation_repo.get_by_id(conversation_id)
        for message in conversation.messages.all().order_by("id"):
            if message.role == "user":
                history.append(HumanMessage(content=message.text or ""))
            elif message.role == "agent":
                history.append(AIMessage(content=message.text or ""))

        return history

    def record_error(self, conversation_id: int):
        error_message = "We couldn't process your request at this time"

        conversation = self.conversation_repo.get_by_id(conversation_id)
        self.message_repo.create(
            conversation=conversation,
            created_at=datetime.now(),
            role="agent",
            text=error_message,
        )
